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
from typing import Iterable
from typing import Tuple

from labm8.py import bazelutil
from labm8.py import test

LLVM_IR_TAR = bazelutil.DataArchive(
  "phd/deeplearning/ml4pl/testing/data/llvm_ir.tar.bz2"
)


def EnumerateLlvmIrs() -> Iterable[Tuple[str, str]]:
  """Enumerate a test set of LLVM IR file paths."""
  with LLVM_IR_TAR as pickled_dir:
    for path in pickled_dir.iterdir():
      with open(path, "r") as f:
        yield path.name, f.read()


@test.Fixture(
  scope="session", params=list(EnumerateLlvmIrs()), namer=lambda s: s[0]
)
def llvm_ir(request) -> str:
  """A test fixture which yields a string of real LLVM IR."""
  return request.param[1]
