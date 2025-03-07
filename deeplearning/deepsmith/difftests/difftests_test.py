# Copyright (c) 2017-2020 Chris Cummins.
#
# DeepSmith is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DeepSmith is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DeepSmith.  If not, see <https://www.gnu.org/licenses/>.
"""Unit tests for //deeplearning/deepsmith/difftests/difftests.py."""
import pytest

import deeplearning.deepsmith.difftests.difftests
from deeplearning.deepsmith.proto import deepsmith_pb2
from labm8.py import app
from labm8.py import test

FLAGS = app.FLAGS

DiffTest = deepsmith_pb2.DifferentialTest
Result = deepsmith_pb2.Result


def test_GoldStandardDiffTester_DiffTestOne_gs_unknown():
  """Test difftest outcomes when gold standard outcome is unknown."""
  dt = deeplearning.deepsmith.difftests.difftests.GoldStandardDiffTester(
    deeplearning.deepsmith.difftests.difftests.NamedOutputIsEqual("stdout")
  )
  assert DiffTest.UNKNOWN == dt.DiffTestOne(
    Result(outcome=Result.UNKNOWN), Result(outcome=Result.UNKNOWN)
  )
  assert DiffTest.UNKNOWN == dt.DiffTestOne(
    Result(outcome=Result.UNKNOWN), Result(outcome=Result.BUILD_FAILURE)
  )
  assert DiffTest.ANOMALOUS_BUILD_FAILURE == dt.DiffTestOne(
    Result(outcome=Result.UNKNOWN), Result(outcome=Result.BUILD_CRASH)
  )
  assert DiffTest.ANOMALOUS_BUILD_FAILURE == dt.DiffTestOne(
    Result(outcome=Result.UNKNOWN), Result(outcome=Result.BUILD_TIMEOUT)
  )
  assert DiffTest.UNKNOWN == dt.DiffTestOne(
    Result(outcome=Result.UNKNOWN), Result(outcome=Result.RUNTIME_CRASH)
  )
  assert DiffTest.UNKNOWN == dt.DiffTestOne(
    Result(outcome=Result.UNKNOWN), Result(outcome=Result.RUNTIME_TIMEOUT)
  )
  assert DiffTest.UNKNOWN == dt.DiffTestOne(
    Result(outcome=Result.UNKNOWN), Result(outcome=Result.PASS)
  )


def test_GoldStandardDiffTester_DiffTestOne_gs_build_failure():
  """Test difftest outcomes when gold standard fails to build."""
  dt = deeplearning.deepsmith.difftests.difftests.GoldStandardDiffTester(
    deeplearning.deepsmith.difftests.difftests.NamedOutputIsEqual("stdout")
  )
  assert DiffTest.UNKNOWN == dt.DiffTestOne(
    Result(outcome=Result.BUILD_FAILURE), Result(outcome=Result.UNKNOWN)
  )
  assert DiffTest.PASS == dt.DiffTestOne(
    Result(outcome=Result.BUILD_FAILURE), Result(outcome=Result.BUILD_FAILURE)
  )
  assert DiffTest.ANOMALOUS_BUILD_FAILURE == dt.DiffTestOne(
    Result(outcome=Result.BUILD_FAILURE), Result(outcome=Result.BUILD_CRASH)
  )
  assert DiffTest.ANOMALOUS_BUILD_FAILURE == dt.DiffTestOne(
    Result(outcome=Result.BUILD_FAILURE), Result(outcome=Result.BUILD_TIMEOUT)
  )
  assert DiffTest.ANOMALOUS_BUILD_PASS == dt.DiffTestOne(
    Result(outcome=Result.BUILD_FAILURE), Result(outcome=Result.RUNTIME_CRASH)
  )
  assert DiffTest.ANOMALOUS_BUILD_PASS == dt.DiffTestOne(
    Result(outcome=Result.BUILD_FAILURE), Result(outcome=Result.RUNTIME_TIMEOUT)
  )
  assert DiffTest.ANOMALOUS_BUILD_PASS == dt.DiffTestOne(
    Result(outcome=Result.BUILD_FAILURE), Result(outcome=Result.PASS)
  )


def test_GoldStandardDiffTester_DiffTestOne_gs_build_crash():
  """Test difftest outcomes when gold standard crahses during build."""
  dt = deeplearning.deepsmith.difftests.difftests.GoldStandardDiffTester(
    deeplearning.deepsmith.difftests.difftests.NamedOutputIsEqual("stdout")
  )
  assert DiffTest.UNKNOWN == dt.DiffTestOne(
    Result(outcome=Result.BUILD_CRASH), Result(outcome=Result.UNKNOWN)
  )
  assert DiffTest.ANOMALOUS_BUILD_FAILURE == dt.DiffTestOne(
    Result(outcome=Result.BUILD_CRASH), Result(outcome=Result.BUILD_CRASH)
  )
  assert DiffTest.ANOMALOUS_BUILD_FAILURE == dt.DiffTestOne(
    Result(outcome=Result.BUILD_CRASH), Result(outcome=Result.BUILD_TIMEOUT)
  )
  assert DiffTest.UNKNOWN == dt.DiffTestOne(
    Result(outcome=Result.BUILD_CRASH), Result(outcome=Result.RUNTIME_CRASH)
  )
  assert DiffTest.UNKNOWN == dt.DiffTestOne(
    Result(outcome=Result.BUILD_CRASH), Result(outcome=Result.RUNTIME_TIMEOUT)
  )
  assert DiffTest.UNKNOWN == dt.DiffTestOne(
    Result(outcome=Result.BUILD_CRASH), Result(outcome=Result.PASS)
  )


def test_GoldStandardDiffTester_DiffTestOne_gs_build_timeout():
  """Test difftest outcomes when gold standard times out during build."""
  dt = deeplearning.deepsmith.difftests.difftests.GoldStandardDiffTester(
    deeplearning.deepsmith.difftests.difftests.NamedOutputIsEqual("stdout")
  )
  assert DiffTest.UNKNOWN == dt.DiffTestOne(
    Result(outcome=Result.BUILD_TIMEOUT), Result(outcome=Result.UNKNOWN)
  )
  assert DiffTest.ANOMALOUS_BUILD_FAILURE == dt.DiffTestOne(
    Result(outcome=Result.BUILD_TIMEOUT), Result(outcome=Result.BUILD_CRASH)
  )
  assert DiffTest.ANOMALOUS_BUILD_FAILURE == dt.DiffTestOne(
    Result(outcome=Result.BUILD_TIMEOUT), Result(outcome=Result.BUILD_TIMEOUT)
  )
  assert DiffTest.UNKNOWN == dt.DiffTestOne(
    Result(outcome=Result.BUILD_TIMEOUT), Result(outcome=Result.RUNTIME_CRASH)
  )
  assert DiffTest.UNKNOWN == dt.DiffTestOne(
    Result(outcome=Result.BUILD_TIMEOUT), Result(outcome=Result.RUNTIME_TIMEOUT)
  )
  assert DiffTest.UNKNOWN == dt.DiffTestOne(
    Result(outcome=Result.BUILD_TIMEOUT), Result(outcome=Result.PASS)
  )


def test_GoldStandardDiffTester_DiffTestOne_gs_runtime_crash():
  """Test difftest outcomes when gold standard crashes at runtime."""
  dt = deeplearning.deepsmith.difftests.difftests.GoldStandardDiffTester(
    deeplearning.deepsmith.difftests.difftests.NamedOutputIsEqual("stdout")
  )
  assert DiffTest.UNKNOWN == dt.DiffTestOne(
    Result(outcome=Result.RUNTIME_CRASH), Result(outcome=Result.UNKNOWN)
  )
  assert DiffTest.ANOMALOUS_BUILD_FAILURE == dt.DiffTestOne(
    Result(outcome=Result.RUNTIME_CRASH), Result(outcome=Result.BUILD_FAILURE)
  )
  assert DiffTest.ANOMALOUS_BUILD_FAILURE == dt.DiffTestOne(
    Result(outcome=Result.RUNTIME_CRASH), Result(outcome=Result.BUILD_CRASH)
  )
  assert DiffTest.ANOMALOUS_BUILD_FAILURE == dt.DiffTestOne(
    Result(outcome=Result.RUNTIME_CRASH), Result(outcome=Result.BUILD_TIMEOUT)
  )
  assert DiffTest.PASS == dt.DiffTestOne(
    Result(outcome=Result.RUNTIME_CRASH), Result(outcome=Result.RUNTIME_CRASH)
  )
  assert DiffTest.PASS == dt.DiffTestOne(
    Result(outcome=Result.RUNTIME_CRASH), Result(outcome=Result.RUNTIME_TIMEOUT)
  )
  assert DiffTest.ANOMALOUS_RUNTIME_PASS == dt.DiffTestOne(
    Result(outcome=Result.RUNTIME_CRASH), Result(outcome=Result.PASS)
  )


def test_GoldStandardDiffTester_DiffTestOne_gs_runtime_timeout():
  """Test difftest outcomes when gold standard times out."""
  dt = deeplearning.deepsmith.difftests.difftests.GoldStandardDiffTester(
    deeplearning.deepsmith.difftests.difftests.NamedOutputIsEqual("stdout")
  )
  assert DiffTest.UNKNOWN == dt.DiffTestOne(
    Result(outcome=Result.RUNTIME_TIMEOUT), Result(outcome=Result.UNKNOWN)
  )
  assert DiffTest.ANOMALOUS_BUILD_FAILURE == dt.DiffTestOne(
    Result(outcome=Result.RUNTIME_TIMEOUT), Result(outcome=Result.BUILD_FAILURE)
  )
  assert DiffTest.ANOMALOUS_BUILD_FAILURE == dt.DiffTestOne(
    Result(outcome=Result.RUNTIME_TIMEOUT), Result(outcome=Result.BUILD_CRASH)
  )
  assert DiffTest.ANOMALOUS_BUILD_FAILURE == dt.DiffTestOne(
    Result(outcome=Result.RUNTIME_TIMEOUT), Result(outcome=Result.BUILD_TIMEOUT)
  )
  assert DiffTest.PASS == dt.DiffTestOne(
    Result(outcome=Result.RUNTIME_TIMEOUT), Result(outcome=Result.RUNTIME_CRASH)
  )
  assert DiffTest.PASS == dt.DiffTestOne(
    Result(outcome=Result.RUNTIME_TIMEOUT),
    Result(outcome=Result.RUNTIME_TIMEOUT),
  )
  assert DiffTest.ANOMALOUS_RUNTIME_PASS == dt.DiffTestOne(
    Result(outcome=Result.RUNTIME_TIMEOUT), Result(outcome=Result.PASS)
  )


def test_GoldStandardDiffTester_DiffTestOne_gs_pass():
  """Test difftest outcomes when gold standard passes."""
  dt = deeplearning.deepsmith.difftests.difftests.GoldStandardDiffTester(
    deeplearning.deepsmith.difftests.difftests.NamedOutputIsEqual("stdout")
  )
  assert DiffTest.UNKNOWN == dt.DiffTestOne(
    Result(outcome=Result.PASS), Result(outcome=Result.UNKNOWN)
  )
  assert DiffTest.ANOMALOUS_BUILD_FAILURE == dt.DiffTestOne(
    Result(outcome=Result.PASS), Result(outcome=Result.BUILD_FAILURE)
  )
  assert DiffTest.ANOMALOUS_BUILD_FAILURE == dt.DiffTestOne(
    Result(outcome=Result.PASS), Result(outcome=Result.BUILD_CRASH)
  )
  assert DiffTest.ANOMALOUS_BUILD_FAILURE == dt.DiffTestOne(
    Result(outcome=Result.PASS), Result(outcome=Result.BUILD_TIMEOUT)
  )
  assert DiffTest.ANOMALOUS_RUNTIME_CRASH == dt.DiffTestOne(
    Result(outcome=Result.PASS), Result(outcome=Result.RUNTIME_CRASH)
  )
  assert DiffTest.ANOMALOUS_RUNTIME_TIMEOUT == dt.DiffTestOne(
    Result(outcome=Result.PASS), Result(outcome=Result.RUNTIME_TIMEOUT)
  )
  assert DiffTest.PASS == dt.DiffTestOne(
    Result(outcome=Result.PASS, outputs={"stdout": "abc"}),
    Result(outcome=Result.PASS, outputs={"stdout": "abc"}),
  )
  assert DiffTest.ANOMALOUS_WRONG_OUTPUT == dt.DiffTestOne(
    Result(outcome=Result.PASS, outputs={"stdout": ""},),
    Result(outcome=Result.PASS, outputs={"stdout": "abc"},),
  )


def test_GoldStandardDiffTester_DiffTestOne_both_pass_no_stdout():
  """Test that error is raised if stdout is missing from output test."""
  dt = deeplearning.deepsmith.difftests.difftests.GoldStandardDiffTester(
    deeplearning.deepsmith.difftests.difftests.NamedOutputIsEqual("stdout")
  )
  with test.Raises(ValueError) as e_ctx:
    dt.DiffTestOne(Result(outcome=Result.PASS), Result(outcome=Result.PASS))
  assert "'stdout' missing in one or more results." == str(e_ctx.value)


if __name__ == "__main__":
  test.Main()
