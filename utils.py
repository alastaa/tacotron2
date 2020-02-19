import numpy as np
import wave
import torch
import re


def get_mask_from_lengths(lengths, use_cpu):
    max_len = torch.max(lengths).item()
    if use_cpu:
        ids = torch.arange(0, max_len, out=torch.LongTensor(max_len))
    else:
        ids = torch.arange(0, max_len, out=torch.cuda.LongTensor(max_len))
    mask = (ids < lengths.unsqueeze(1)).byte()
    return mask


def load_wav_to_torch(full_path):
    sampling_rate,_, data = readwav(full_path)
    return torch.FloatTensor(data.astype(np.float32)), sampling_rate


def load_filepaths_and_text(filenames, split="|", speaker_id=None,
                            audio_path_regex=None):
    speaker_id_mapping = {0: '01m', 1: '02m',2: '03m', 3: '01n',4: '02n', 5: '03n'}
    all_filepaths_and_text = []
    for filename in filenames:
        with open(filename, encoding='utf-8') as f:
            if speaker_id is not None:
                filepaths_and_text = [line.strip().split(split) for line in f
                                      if speaker_id_mapping[speaker_id] in line.split(split)[0]]
            else:
                filepaths_and_text = [line.strip().split(split) for line in f]

        if audio_path_regex is not None:
            filepaths_and_text = [ft for ft in filepaths_and_text
                                  if re.search(audio_path_regex, ft[0])]
        all_filepaths_and_text.extend(filepaths_and_text)

    return all_filepaths_and_text


def to_gpu(x):
    x = x.contiguous()

    if torch.cuda.is_available():
        x = x.cuda(non_blocking=True)
    return torch.autograd.Variable(x)


def _wav2array(nchannels, sampwidth, data):
    """data must be the string containing the bytes from the wav file."""
    num_samples, remainder = divmod(len(data), sampwidth * nchannels)
    if remainder > 0:
        raise ValueError('The length of data is not a multiple of '
                         'sampwidth * num_channels.')
    if sampwidth > 4:
        raise ValueError("sampwidth must not be greater than 4.")

    if sampwidth == 3:
        a = np.empty((num_samples, nchannels, 4), dtype=np.uint8)
        raw_bytes = np.fromstring(data, dtype=np.uint8)
        a[:, :, :sampwidth] = raw_bytes.reshape(-1, nchannels, sampwidth)
        a[:, :, sampwidth:] = (a[:, :, sampwidth - 1:sampwidth] >> 7) * 255
        result = a.view('<i4').reshape(a.shape[:-1])
    else:
        # 8 bit samples are stored as unsigned ints; others as signed ints.
        dt_char = 'u' if sampwidth == 1 else 'i'
        a = np.fromstring(data, dtype='<%s%d' % (dt_char, sampwidth))
        result = a.reshape(-1, nchannels)
    return result


def readwav(file):
    """
    Read a wav file.
    Returns the frame rate, sample width (in bytes) and a numpy array
    containing the data.
    This function does not read compressed wav files.
    """
    wav = wave.open(file)
    rate = wav.getframerate()
    nchannels = wav.getnchannels()
    sampwidth = wav.getsampwidth()
    nframes = wav.getnframes()
    data = wav.readframes(nframes)
    wav.close()
    array = _wav2array(nchannels, sampwidth, data)
    return rate, sampwidth, array
