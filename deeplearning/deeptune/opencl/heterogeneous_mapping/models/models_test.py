# Copyright (c) 2017-2020 Chris Cummins.
#
# DeepTune is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DeepTune is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DeepTune.  If not, see <https://www.gnu.org/licenses/>.
"""Unit tests for //deeplearning/deeptune/opencl/heterogeneous_mapping:models."""
from deeplearning.deeptune.opencl.heterogeneous_mapping.models import models
from labm8.py import test

MODULE_UNDER_TEST = None  # No coverage.


def test_num_models():
  """Test that the number of models. This will change"""
  assert len(models.ALL_MODELS) == 5


if __name__ == "__main__":
  test.Main()
