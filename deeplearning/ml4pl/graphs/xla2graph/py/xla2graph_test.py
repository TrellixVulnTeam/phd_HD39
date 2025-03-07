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
"""Unit tests for //deeplearning/ml4pl/graphs/xla2graph/py:xla2graph."""
from tensorflow.compiler.xla.service import hlo_pb2

from deeplearning.ml4pl.graphs.xla2graph.py import xla2graph
from labm8.py import app
from labm8.py import bazelutil
from labm8.py import pbutil
from labm8.py import test


FLAGS = app.FLAGS

TEST_PROTO = bazelutil.DataPath(
  "phd/deeplearning/ml4pl/testing/data/hlo/a.hlo.pb"
)


def test_empty_proto():
  """Build from an empty proto."""
  proto = hlo_pb2.HloProto()
  with test.Raises(RuntimeError) as e_ctx:
    xla2graph.BuildProgramGraphProto(proto)

  assert "Failed to locate entry computation" in str(e_ctx.value)


def test_non_empty_proto():
  """Build a graph proto from an example proto."""
  proto = pbutil.FromFile(TEST_PROTO, hlo_pb2.HloProto())
  graph = xla2graph.BuildProgramGraphProto(proto)
  assert len(graph.node) == 155
  assert len(graph.function) == 5


def test_non_empty_proto_to_networkx():
  """Build a networkx graph from an example proto."""
  proto = pbutil.FromFile(TEST_PROTO, hlo_pb2.HloProto())
  graph = xla2graph.BuildProgramGraphNetworkX(proto)
  assert graph.number_of_nodes() == 155


if __name__ == "__main__":
  test.Main()
