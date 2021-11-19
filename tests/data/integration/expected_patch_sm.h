/*
 * MIT License
 * 
 * Copyright (c) 2021 Electrosmith
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#ifndef __JSON2DAISY_PATCH_SM_H__
#define __JSON2DAISY_PATCH_SM_H__

#include "daisy_patch_sm.h"


#define ANALOG_COUNT 0

namespace json2daisy {



struct DaisyPatch_sm {

  /** Initializes the board according to the JSON board description
   *  \param boost boosts the clock speed from 400 to 480 MHz
   */
  void Init(bool boost=true) 
  {
    som.Init();

    // Display
    // no display 


  }

  /** Handles all the controls processing that needs to occur at the block rate
   * 
   */
  void ProcessAllControls() 
  {
    som.ProcessAllControls();
  }

  /** Handles all the maintenance processing. This should be run last within the audio callback.
   * 
   */
  void PostProcess()
  {
    
  }

  /** Sets the audio sample rate
   *  \param sample_rate the new sample rate in Hz
   */
  void SetAudioSampleRate(size_t sample_rate) 
  {
    som.SetAudioSampleRate(sample_rate);
    
  }

  /** Sets the audio block size
   *  \param block_size the new block size in words
   */
  inline void SetAudioBlockSize(size_t block_size) 
  {
    som.SetAudioBlockSize(block_size);
  }

  /** Starts up the audio callback process with the given callback
   * 
   */
  inline void StartAudio(daisy::AudioHandle::AudioCallback cb)
  {
    som.StartAudio(cb);
  }

  /** This is the board's "System On Module"
   */
  daisy::patch_sm::DaisyPatchSM som;

  // I/O Components
  
  // no display

};

} // namspace json2daisy

#endif // __JSON2DAISY_PATCH_SM_H__