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
"""Unit tests for //deeplearning/ml4pl/models:log_analysis."""
import random
from typing import List
from typing import NamedTuple

import numpy as np
import sqlalchemy as sql

from deeplearning.ml4pl import run_id as run_id
from deeplearning.ml4pl.graphs.labelled import graph_tuple_database
from deeplearning.ml4pl.models import log_analysis
from deeplearning.ml4pl.models import log_database
from deeplearning.ml4pl.testing import random_graph_tuple_database_generator
from deeplearning.ml4pl.testing import random_log_database_generator
from deeplearning.ml4pl.testing import testing_databases
from labm8.py import decorators
from labm8.py import test


FLAGS = test.FLAGS

###############################################################################
# Fixtures.
###############################################################################


@test.Fixture(
  scope="session", params=((0, 2), (2, 0)), names=("node_y=2", "graph_y=2")
)
def graph_db(request) -> graph_tuple_database.Database:
  """A test fixture which returns a graph database with random graphs."""
  graph_y_dimensionality, node_y_dimensionality = request.param
  db = graph_tuple_database.Database(testing_databases.GetDatabaseUrls()[0])
  random_graph_tuple_database_generator.PopulateDatabaseWithRandomGraphTuples(
    db,
    graph_count=100,
    graph_y_dimensionality=graph_y_dimensionality,
    node_y_dimensionality=node_y_dimensionality,
  )
  return db


@test.Fixture(scope="session")
def generator(
  graph_db: graph_tuple_database.Database,
) -> random_log_database_generator.RandomLogDatabaseGenerator:
  """A test fixture which returns a log generator."""
  return random_log_database_generator.RandomLogDatabaseGenerator(graph_db)


@test.Fixture(
  scope="session",
  params=testing_databases.GetDatabaseUrls(),
  namer=testing_databases.DatabaseUrlNamer("log_db"),
)
def empty_log_db(request) -> log_database.Database:
  """A test fixture which yields an empty log database."""
  yield from testing_databases.YieldDatabase(
    log_database.Database, request.param
  )


class DatabaseAndRunIds(NamedTuple):
  """A populated log database and the run IDs used to populate it."""

  db: log_database.Database
  run_ids: List[run_id.RunId]


@test.Fixture(
  scope="session",
  params=testing_databases.GetDatabaseUrls(),
  namer=testing_databases.DatabaseUrlNamer("log_db"),
)
def populated_log_db(
  request, generator: random_log_database_generator.RandomLogDatabaseGenerator
) -> DatabaseAndRunIds:
  """A test fixture which yields an empty log database."""
  with testing_databases.DatabaseContext(
    log_database.Database, request.param
  ) as db:
    yield DatabaseAndRunIds(
      db=db, run_ids=generator.PopulateLogDatabase(db, run_count=10)
    )


###############################################################################
# LogAnalyzer Tests.
###############################################################################


def test_LogAnalyzer_empty_db(empty_log_db: log_database.Database):
  """Test that log analyzer works on an empty database."""
  with test.Raises(ValueError):
    log_analysis.LogAnalyzer(empty_log_db)


###############################################################################
# RunLogAnalyser Tests.
###############################################################################


def test_RunLogAnalyser_smoke_tests(populated_log_db: DatabaseAndRunIds):
  """Black-box test that run log properties work."""
  for run_id in populated_log_db.run_ids:
    run = log_analysis.RunLogAnalyzer(populated_log_db.db, run_id)
    assert run.graph_db
    assert run.tables.keys() == {"parameters", "epochs", "runs", "tags"}


def test_RunLogAnalyser_empty_db(empty_log_db: log_database.Database):
  """Test that cannot analyse non-existing run."""
  with test.Raises(ValueError):
    log_analysis.RunLogAnalyzer(
      empty_log_db, run_id.RunId.GenerateUnique("foo")
    )


def test_RunLogAnalyser_smoke_tests(populated_log_db: DatabaseAndRunIds):
  """Black-box test that run log properties work."""
  for run_id in populated_log_db.run_ids:
    run = log_analysis.RunLogAnalyzer(populated_log_db.db, run_id)
    assert run.graph_db
    assert run.tables.keys() == {"parameters", "epochs", "runs", "tags"}


@test.Parametrize(
  "metric",
  (
    "best accuracy",
    "best precision",
    "best recall",
    "best f1",
    "90% val acc",
    "95% val acc",
    "99.9% val acc",
  ),
)
def test_RunLogAnalyser_best_epoch_num(
  populated_log_db: DatabaseAndRunIds, metric: str
):
  """Black-box test that run log properties work."""
  for run_id in populated_log_db.run_ids:
    run = log_analysis.RunLogAnalyzer(populated_log_db.db, run_id)
    try:
      assert run.GetBestEpochNum(metric=metric)
    except ValueError as e:
      # Some metrics will raise an error if they are not met. This is fine.
      assert str(e) == f"No {run_id} epochs reached {metric}"


def test_GetGraphsForBatch(populated_log_db: DatabaseAndRunIds):
  """Test reconstructing graphs from a detailed batch."""
  # Select a random run to analyze.
  run_id = random.choice(populated_log_db.run_ids)
  run = log_analysis.RunLogAnalyzer(populated_log_db.db, run_id)

  with populated_log_db.db.Session() as session:
    # Select some random detailed batches to reconstruct the graphs of.
    detailed_batches = (
      session.query(log_database.Batch)
      .join(log_database.BatchDetails)
      .options(sql.orm.joinedload(log_database.Batch.details))
      .order_by(populated_log_db.db.Random())
      .limit(50)
      .all()
    )
    # Sanity check that there are detailed batches.
    assert detailed_batches

  for batch in detailed_batches:
    graphs = list(run.GetGraphsForBatch(batch))
    # Check that the number of graphs returned matches the unique batch graph
    # count.
    assert len(graphs) == len(set(batch.graph_ids))


def test_GetInputOutputGraphs(populated_log_db: DatabaseAndRunIds):
  """Test reconstructing graphs from a detailed batch."""
  # Select a random run to analyze.
  run_id = random.choice(populated_log_db.run_ids)
  run = log_analysis.RunLogAnalyzer(populated_log_db.db, run_id)

  with populated_log_db.db.Session() as session:
    # Select some random detailed batches to reconstruct the graphs of.
    detailed_batches = (
      session.query(log_database.Batch)
      .join(log_database.BatchDetails)
      .options(sql.orm.joinedload(log_database.Batch.details))
      .order_by(populated_log_db.db.Random())
      .limit(50)
      .all()
    )
    # Sanity check that there are detailed batches.
    assert detailed_batches

  for batch in detailed_batches:
    input_output_graphs = list(run.GetInputOutputGraphs(batch))
    # Check that the number of input_output_graphs matches the size of the
    # batch.
    assert len(input_output_graphs) == len(batch.graph_ids)


def test_BuildConfusionMatrix():
  """Test confusion matrix with known values."""
  confusion_matrix = log_analysis.BuildConfusionMatrix(
    targets=np.array(
      [
        np.array([1, 0, 0], dtype=np.int32),
        np.array([0, 0, 1], dtype=np.int32),
        np.array([0, 0, 1], dtype=np.int32),
      ]
    ),
    predictions=np.array(
      [
        np.array([0.1, 0.5, 0], dtype=np.float32),
        np.array([0, -0.5, -0.3], dtype=np.float32),
        np.array([0, 0, 0.8], dtype=np.float32),
      ]
    ),
  )

  assert confusion_matrix.shape == (3, 3)
  assert confusion_matrix.sum() == 3
  assert np.array_equal(
    confusion_matrix, np.array([[0, 1, 0], [0, 0, 0], [1, 0, 1],])
  )


@decorators.loop_for(seconds=10)
def test_fuzz_BuildConfusionMatrix():
  """Fuzz confusion matrix construction."""
  num_instances = random.randint(1, 100)
  y_dimensionality = random.randint(2, 5)

  targets = np.random.rand(num_instances, y_dimensionality)
  predictions = np.random.rand(num_instances, y_dimensionality)

  confusion_matrix = log_analysis.BuildConfusionMatrix(targets, predictions)

  assert confusion_matrix.shape == (y_dimensionality, y_dimensionality)
  assert confusion_matrix.sum() == num_instances


if __name__ == "__main__":
  test.Main()
