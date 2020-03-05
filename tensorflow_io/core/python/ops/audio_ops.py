# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Audio Ops."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

from tensorflow_io.core.python.ops import core_ops

def decode(contents, desired_channels=-1, desired_samples=-1, name=None):
  """
  Decode audio data to an int16 tensor.

  Tries to determine the format automatically.
  Currently supported: MP3

  Args:
    contents: A `Tensor` of type `string`. 0-D. The encoded data.
    desired_channels: An integer determining the number of channels in the
        output. If this number is greater than the number of channels in the
        source, they are duplicated. If it is smaller, only the first is used.
    desired_samples: An integer determining the number of samples in the ouput
        (per channel). If this number is greater than the number of samples
        in the source, the output is 0-padded on the right. If it is smaller,
        the output is truncated.
    name: A name for the operation (optional).

  Returns:
    A `Tensor` of type `int16` and shape of `[channels, samples]` and a scalar
    `Tensor` of type `int32` containing the sample rate of the MP3.
  """
  samples, sample_rate = core_ops.io_audio_decode(contents, name=name)
  samples = _fix_shape(samples, desired_channels, desired_samples)
  return samples, sample_rate


def decode_mp3(contents, desired_channels=-1, desired_samples=-1, name=None):
  """
  Decode MP3 data to an int16 tensor.

  Args:
    contents: A `Tensor` of type `string`. 0-D. The encoded MP3.
    desired_channels: An integer determining the number of channels in the
        output. If this number is greater than the number of channels in the
        source, they are duplicated. If it is smaller, only the first is used.
    desired_samples: An integer determining the number of samples in the ouput
        (per channel). If this number is greater than the number of samples
        in the source, the output is 0-padded on the right. If it is smaller,
        the output is truncated.
    name: A name for the operation (optional).

  Returns:
    A `Tensor` of type `int16` and shape of `[channels, samples]` and a scalar
    `Tensor` of type `int32` containing the sample rate of the MP3.
  """
  samples, sample_rate = core_ops.io_audio_decode_mp3(contents, name=name)
  samples = _fix_shape(samples, desired_channels, desired_samples)
  return samples, sample_rate


def _fix_shape(data, desired_channels, desired_samples):
  """Fix shape of decoded audio to desired channels and samples."""
  org_shape = tf.shape(data)
  org_samples = org_shape[1]

  if desired_samples >= 0:
    # truncate if necessary
    # ignored if org_samples <= desired_samples
    data = data[:, :desired_samples]

    # pad if necessary
    right_pad = desired_samples - org_samples
    if right_pad > 0:
      data = tf.pad(data, [[0, 0], [0, right_pad]], "CONSTANT")

  if desired_channels >= 0:
    out_samples = desired_samples if desired_samples >= 0 else org_samples

    # truncate if necessary
    # ignored if org_channels <= desired_channels
    data = data[:desired_channels, :]

    # convert to mono to stereo if necessary
    data = tf.broadcast_to(data, [desired_channels, out_samples])

  return data
