# Copyright 2019-2020 the ProGraML authors.
#
# Contact Chris Cummins <chrisc.101@gmail.com>.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Base class for implementing classifier models."""
import copy
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Set

import pandas as pd

from deeplearning.ml4pl import run_id as run_id_lib
from deeplearning.ml4pl.graphs.labelled import graph_database_reader
from deeplearning.ml4pl.graphs.labelled import graph_tuple_database
from deeplearning.ml4pl.models import batch as batches
from deeplearning.ml4pl.models import checkpoints
from deeplearning.ml4pl.models import epoch
from deeplearning.ml4pl.models import logger as logging
from labm8.py import app
from labm8.py import decorators
from labm8.py import gpu_scheduler
from labm8.py import humanize
from labm8.py import progress


FLAGS = app.FLAGS


app.DEFINE_boolean(
  "strict_graph_segmentation",
  False,
  "If set, strictly enforce that graphs do not cross the "
  "{train,val,test} epoch boundaries. This is disabled by default as the "
  "performance and memory overhead may be large for big datasets.",
)
app.DEFINE_integer(
  "max_data_flow_steps",
  0,
  "If set to a positive value, limit the size of dataflow-annotated graphs "
  "used to only those with data_flow_steps <= --max_data_flow_steps. "
  "This has no effect for graph databases with no dataflow annotations.",
)


class ClassifierBase(object):
  """Abstract base class for implementing classifiers.

  Before using the model, it must be initialized bu calling Initialize(), or
  restored from a checkpoint using RestoreFrom(checkpoint).

  Subclasses must implement the following methods:
    MakeBatch()        # construct a batch from input graphs.
    RunBatch()         # run the model on the batch.
    GetModelData()     # get model data to save.
    LoadModelData()    # load model data.

  And may optionally wish to implement these additional methods:
    CreateModelData()  # initialize an untrained model.
    Summary()          # return a string model summary.
    GraphReader()      # return a buffered graph reader.
    BatchIterator()    # return an iterator over batches.
  """

  def __init__(
    self,
    logger: logging.Logger,
    graph_db: graph_tuple_database.Database,
    run_id: Optional[run_id_lib.RunId] = None,
  ):
    """Constructor.

    This creates an uninitialized model. Initialize the model before use by
    calling Initialize() or RestoreFrom(checkpoint).

    Args:
      logger: A logger to write {batch, epoch, checkpoint} data to.
      graph_db: The graph database which will be used to feed inputs to the
        model.

    Raises:
      NotImplementedError: If both node and graph labels are set.
      TypeError: If neither graph or node labels are set.
      ValueError: If graph_db is empty.
    """
    if not graph_db.graph_count:
      raise ValueError(f"Database contains no graphs: {graph_db}")

    # Sanity check the dimensionality of input graphs.
    if (
      not graph_db.node_y_dimensionality and not graph_db.graph_y_dimensionality
    ):
      raise NotImplementedError(
        "Neither node ory" " graph labels are set. What am I to do?"
      )
    if graph_db.node_y_dimensionality and graph_db.graph_y_dimensionality:
      raise NotImplementedError(
        "Both node and graph labels are set. This is currently not supported. "
        "See <github.com/ChrisCummins/ProGraML/issues/26>"
      )

    # Model properties.
    self.logger: logging.Logger = logger
    self.graph_db: graph_tuple_database.Database = graph_db
    self.run_id: run_id_lib.RunId = (
      run_id or run_id_lib.RunId.GenerateUnique(type(self).__name__)
    )
    self.y_dimensionality: int = (
      self.graph_db.node_y_dimensionality
      or self.graph_db.graph_y_dimensionality
    )

    # Set by Initialize() and RestoredFrom()
    self._initialized = False
    self.restored_from: Optional[checkpoints.CheckpointReference] = None

    # Progress counters that are saved and loaded from checkpoints.
    self.epoch_num = 0
    self.best_results: Dict[epoch.Type, epoch.BestResults] = {
      epoch.Type.TRAIN: epoch.BestResults(),
      epoch.Type.VAL: epoch.BestResults(),
      epoch.Type.TEST: epoch.BestResults(),
    }

    # If --strict_graph_segmentation is set, check for graphs that we have
    # already seen before by keep a log of all unique graph IDs of each type.
    self.graph_ids: Dict[epoch.Type, Set[int]] = {
      epoch.Type.TRAIN: set(),
      epoch.Type.VAL: set(),
      epoch.Type.TEST: set(),
    }

    # Get exclusive access to a GPU, if available. Do this before calling
    # logger.OnStartRun() since this changes the environment variables.
    self.gpu = gpu_scheduler.LockExclusiveProcessGpuAccess()

    # Register this model with the logger.
    self.logger.OnStartRun(self.run_id, self.graph_db)

  def __del__(self):
    # Defensively check for gpu attribute since __del__ is called even if
    # __init__ throws an error and does not complete.
    if hasattr(self, "gpu") and self.gpu:
      gpu_scheduler.GetDefaultScheduler().ReleaseGpu(self.gpu)

  #############################################################################
  # Interface methods. Subclasses must implement these.
  #############################################################################

  def MakeBatch(
    self,
    epoch_type: epoch.Type,
    graphs: Iterable[graph_tuple_database.GraphTuple],
    ctx: progress.ProgressContext = progress.NullContext,
  ) -> batches.Data:
    """Create a mini-batch of data from an iterator of graphs.

    Implementations of this method must be thread safe. Multiple threads may
    concurrently call this method using different graph iterators. This is to
    amortize I/O costs when alternating between training / validation / testing
    datasets.

    Returns:
      A single batch of data for feeding into RunBatch(). A batch consists of a
      list of graph IDs and a model-defined blob of data. If the list of graph
      IDs is empty, the batch is discarded and not fed into RunBatch(). If the
      end_of_batches flag is set, the batch data is not read.
    """
    raise NotImplementedError("abstract class")

  def RunBatch(
    self,
    epoch_type: epoch.Type,
    batch: batches.Data,
    ctx: progress.ProgressContext = progress.NullContext,
  ) -> batches.Results:
    """Process a mini-batch of data using the model.

    Args:
      log: The mini-batch log returned by MakeBatch().
      batch: The batch data returned by MakeBatch().

    Returns:
      The target values for the batch, and the predicted values.
    """
    raise NotImplementedError("abstract class")

  def CreateModelData(self) -> None:
    """Initialize the starting state of a model.

    Use this method to perform any model-specific initialisation such as
    randomizing starting weights. When restoring a model from a checkpoint, this
    method is *not* called. Instead, LoadModelData() will be called.

    Note that subclasses must call this superclass method first.
    """
    pass

  def LoadModelData(self, data_to_load: Any) -> None:
    """Set the model state from the given model data.

    Args:
      data_to_load: The return value of GetModelData().
    """
    raise NotImplementedError("abstract class")

  def GetModelData(self) -> Any:
    """Return the model state.

    Returns:
      A  model-defined blob of data that can later be passed to LoadModelData()
      to restore the current model state.
    """
    raise NotImplementedError("abstract class")

  def Summary(self) -> str:
    """Return a long summary string describing the model."""
    return type(self).__name__

  #############################################################################
  # Automatic methods.
  #############################################################################

  def __call__(
    self,
    epoch_type: epoch.Type,
    batch_iterator: batches.BatchIterator,
    logger: logging.Logger,
    epoch_name_prefix: str = "",
  ) -> epoch.Results:
    """Run the model for over the input batches.

    This is the heart of the model - where you run an epoch of batches through
    the graph and produce results. The interface for training and inference is
    the same, only the epoch_type value should change.

    Side effects of calling a model are:
      * The model bumps its epoch_num counter if on a training epoch.
      * The model updates its best_results dictionary if the accuracy produced
        by this epoch is greater than the previous best.

    Args:
      epoch_type: The type of epoch to run.
      batch_iterator: The batches to process.
      logger: A logger instance to log results to.
      epoch_name_prefix: An optional prefix for the name of the epoch.

    Returns:
      An epoch results instance.
    """
    if not self._initialized:
      raise TypeError(
        "Model called before Initialize() or FromCheckpoint() invoked"
      )

    # Only training epochs bumps the epoch count.
    if epoch_type == epoch.Type.TRAIN:
      self.epoch_num += 1

    thread = EpochThread(
      self,
      epoch_type,
      batch_iterator,
      logger,
      epoch_name_prefix=epoch_name_prefix,
    )
    progress.Run(thread)

    # Check that there were batches.
    if not thread.batch_count:
      raise ValueError("No batches")

    # If --strict_graph_segmentation is set, check for graphs that we have
    # already seen before.
    if FLAGS.strict_graph_segmentation:
      with logger.ctx.Profile(4, "Checked strict graph segmentation"):
        for other_epoch_type in set(list(epoch.Type)) - {epoch_type}:
          duplicate_graph_ids = self.graph_ids[other_epoch_type].intersection(
            thread.graph_ids
          )
          if duplicate_graph_ids:
            raise ValueError(
              f"{epoch_type} batch contains {len(duplicate_graph_ids)} graphs "
              f"from {other_epoch_type}: {list(duplicate_graph_ids)[:100]}"
            )
        self.graph_ids[epoch_type] = self.graph_ids[epoch_type].union(
          thread.graph_ids
        )

    # TODO(github.com/ChrisCummins/ProGraML/issues/38): Explicitly free the
    # thread object to see if that is contributing to climbing memory usage.
    results = copy.deepcopy(thread.results)
    if not results:
      raise OSError("Epoch produced no results. Did the model crash?")
    del thread

    # Update the record of best results.
    if results > self.best_results[epoch_type].results:
      new_best = epoch.BestResults(epoch_num=self.epoch_num, results=results)
      logger.ctx.Log(
        2,
        "%s results improved from %s",
        epoch_type.name.capitalize(),
        self.best_results[epoch_type],
      )
      self.best_results[epoch_type] = new_best

    return results

  def GraphReader(
    self,
    epoch_type: epoch.Type,
    graph_db: graph_tuple_database.Database,
    filters: Optional[List[Callable[[], bool]]] = None,
    limit: Optional[int] = None,
    ctx: progress.ProgressContext = progress.NullContext,
  ) -> graph_database_reader.BufferedGraphReader:
    """Construct a buffered graph reader.

    Args:
      epoch_type: The type of graph reader to return a graph reader for.
      graph_db: The graph database to read graphs from.
      filters: A list of filters to impose on the graph database reader.
      limit: The maximum number of rows to read.
      ctx: A logging context.

    Returns:
      A buffered graph reader instance.
    """
    del epoch_type

    filters = filters or []

    # Optionally limit graphs to data_flow_steps <= --max_data_flow_steps.
    if FLAGS.max_data_flow_steps and self.graph_db.has_data_flow:
      filters.append(
        lambda: graph_tuple_database.GraphTuple.data_flow_steps
        <= FLAGS.max_data_flow_steps
      )

    return graph_database_reader.BufferedGraphReader.CreateFromFlags(
      graph_db=graph_db,
      filters=filters,
      ctx=ctx,
      limit=limit,
      eager_graph_loading=True,
    )

  def BatchIterator(
    self,
    epoch_type: epoch.Type,
    graphs: Iterable[graph_tuple_database.GraphTuple],
    ctx: progress.ProgressContext = progress.NullContext,
  ) -> Iterable[batches.Data]:
    """Generate model batches from a iterator of graphs.

    Args:
      epoch_type: The type of epoch that batches are being constructed for.
      graphs: The graphs to construct batches from.
      ctx: A logging context.

    Returns:
      A batch iterator.
    """
    while True:
      with ctx.Profile(
        4,
        lambda t: (
          f"Constructed batch of "
          f"{humanize.Plural(batch.graph_count, f'{epoch_type.name.lower()} graph')}"
        ),
      ):
        batch = self.MakeBatch(epoch_type, graphs)

      # We have reached the end of the inputs.
      if batch.end_of_batches:
        break

      yield batch

  def Initialize(self) -> None:
    """Initialize an untrained model."""
    if self._initialized:
      raise TypeError("CreateModelData() called on already-initialized model")

    self._initialized = True
    self.CreateModelData()

  def RestoreFrom(self, checkpoint_ref: checkpoints.CheckpointReference):
    """Restore a model from a checkpoint."""
    self._initialized = True
    self.restored_from = checkpoint_ref
    checkpoint = self.logger.Load(checkpoint_ref)
    self.epoch_num = checkpoint.epoch_num
    self.best_results = checkpoint.best_results
    self.LoadModelData(checkpoint.model_data)

  def SaveCheckpoint(self) -> checkpoints.CheckpointReference:
    """Construct a checkpoint from the current model state.

    Returns:
      A checkpoint reference.
    """
    if not self._initialized:
      raise TypeError("Cannot save an unitialized model.")

    self.logger.Save(
      checkpoints.Checkpoint(
        run_id=self.run_id,
        epoch_num=self.epoch_num,
        best_results=self.best_results,
        model_data=self.GetModelData(),
      )
    )
    return checkpoints.CheckpointReference(
      run_id=self.run_id, tag=None, epoch_num=self.epoch_num
    )

  @decorators.memoized_property
  def parameters(self) -> pd.DataFrame:
    return self.logger.GetParameters(self.run_id)


class EpochThread(progress.Progress):
  """A thread which runs a single epoch of a model.

  After running this thread, the results of the epoch may be accessed through
  the 'results' parameter.
  """

  def __init__(
    self,
    model: ClassifierBase,
    epoch_type: epoch.Type,
    batch_iterator: batches.BatchIterator,
    logger: logging.Logger,
    epoch_name_prefix: str = "",
  ):
    """Constructor.

    Args:
      model: A model instance.
      epoch_type: The type of epoch to run.
      batch_iterator: A batch iterator.
      logger: A logger.
    """
    self.model = model
    self.epoch_type = epoch_type
    self.batch_iterator = batch_iterator
    self.logger = logger
    self.batch_count = 0

    # Set at the end of Run().
    self.results: epoch.Results = None
    self.graph_ids = set()

    super(EpochThread, self).__init__(
      name=(
        f"{epoch_name_prefix}{epoch_type.name.capitalize()} "
        f"epoch {model.epoch_num}"
      ),
      i=0,
      n=batch_iterator.graph_count,
      unit="graph",
      vertical_position=0,
      leave=False,
    )

  def Run(self) -> None:
    """Run the epoch worker thread."""
    rolling_results = batches.RollingResults()

    for i, batch in enumerate(self.batch_iterator.batches):
      self.batch_count += 1
      self.ctx.i += batch.graph_count

      # Record the unique graph IDs.
      for graph_id in batch.graph_ids:
        self.graph_ids.add(graph_id)

      # We have run out of batches.
      if batch.end_of_batches:
        break

      # Skip an empty batch.
      if not batch.graph_count:
        continue

      # Run the batch through the model.
      with self.ctx.Profile(
        3,
        lambda t: (
          f"Batch {i+1} with "
          f"{batch.graph_count} graphs: "
          f"{batch_results}"
        ),
      ) as batch_timer:
        batch_results = self.model.RunBatch(self.epoch_type, batch)

      # Record the batch results.
      self.logger.OnBatchEnd(
        run_id=self.model.run_id,
        epoch_type=self.epoch_type,
        epoch_num=self.model.epoch_num,
        batch_num=i + 1,
        timer=batch_timer,
        data=batch,
        results=batch_results,
      )
      rolling_results.Update(
        batch, batch_results, weight=batch_results.target_count
      )
      self.ctx.bar.set_postfix(
        loss=rolling_results.loss,
        acc=rolling_results.accuracy,
        prec=rolling_results.precision,
        rec=rolling_results.recall,
      )

    self.results = epoch.Results.FromRollingResults(rolling_results)
    self.logger.OnEpochEnd(
      self.model.run_id, self.epoch_type, self.model.epoch_num, self.results
    )
