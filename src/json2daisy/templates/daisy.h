#ifndef __JSON2DAISY_{{name|upper}}_H__
#define __JSON2DAISY_{{name|upper}}_H__

{% if som == 'seed' %}
#include "daisy_seed.h"
{% elif som == 'patch_sm' %}
#include "daisy_patch_sm.h"
{% endif %}

namespace json2daisy {

struct Daisy{{ name|capitalize }} {

  /** Initializes the board according to the JSON board description
   *  \param boost boosts the clock speed from 400 to 480 MHz
   */
  void Init(bool boost=true) 
  {
    {% if som == 'seed' %}
    som.Configure();
    som.Init(boost);
    {% else %}
    som.Init();
    {% endif %}

    {% if init != '' %} 
    {{init}} 
    {% endif %}
    {% if i2c != '' %}
    // i2c
    {{ i2c }} 
    {% endif %}
    {% if pca9685 != '' %} 
    // LED Drivers
    {{ pca9685 }} 
    {% endif %}
    {% if switch != '' %} 
    // Switches
    {{ switch }} 
    {% endif %}
    {% if switch3 != '' %}
    // SPDT Switches
    {{ switch3 }} 
    {% endif %}
    {% if cd4021 != '' %} 
    // Muxes
    {{ cd4021 }} 
    {% endif %}
    {% if gatein != '' %} 
    // Gate ins
    {{ gatein }} 
    {% endif %}
    {% if encoder != '' %} 
    // Rotary encoders
    {{ encoder }} 
    {% endif %}
    {% if init_single != '' %} 
    // Single channel ADC initialization
    {{ init_single }} 
    {% endif %}
    {% if som == 'seed' %}
    som.adc.Init(cfg, ANALOG_COUNT);
    {% endif %}
    {% if ctrl_init != '' %} 
    // AnalogControl objects
    {{ ctrl_init }} 
    {% endif %}
    {% if ctrl_mux_init != '' %} 
    // Multiplexed AnlogControl objects
    {{ ctrl_mux_init }} 
    {% endif %}
    {% if led != '' %} 
    // LEDs
    {{ led }} 
    {% endif %}
    {% if rgbled != '' %}
    // RBG LEDs 
    {{ rgbled }} 
    {% endif %}
    {% if gateout != '' %} 
    // Gate outs
    {{ gateout }} 
    {% endif %}
    {% if dachandle != '' %}
    // DAC 
    {{ dachandle }} 
    {% endif %}
    {% if display != '' %}
    // Display
    {{ display }} 
    {% endif %}

    {% if som == 'seed' and external_codecs|length > 0 %}
    // External Codec Initialization
    SaiHandle::Config sai_config[{{ 1 + external_codecs|length }}];

    // Internal Codec
    sai_config[0].periph          = SaiHandle::Config::Peripheral::SAI_1;
    sai_config[0].sr              = SaiHandle::Config::SampleRate::SAI_48KHZ;
    sai_config[0].bit_depth       = SaiHandle::Config::BitDepth::SAI_24BIT;
    sai_config[0].a_sync          = SaiHandle::Config::Sync::MASTER;
    sai_config[0].b_sync          = SaiHandle::Config::Sync::SLAVE;
    sai_config[0].a_dir           = SaiHandle::Config::Direction::TRANSMIT;
    sai_config[0].b_dir           = SaiHandle::Config::Direction::RECEIVE;
    sai_config[0].pin_config.fs   = {DSY_GPIOE, 4};
    sai_config[0].pin_config.mclk = {DSY_GPIOE, 2};
    sai_config[0].pin_config.sck  = {DSY_GPIOE, 5};
    sai_config[0].pin_config.sa   = {DSY_GPIOE, 6};
    sai_config[0].pin_config.sb   = {DSY_GPIOE, 3};

    {% for codec in external_codecs %}
    sai_config[{{loop.index}}].periph          = SaiHandle::Config::Peripheral::{{codec.periph}};
    sai_config[{{loop.index}}].sr              = SaiHandle::Config::SampleRate::SAI_48KHZ;
    sai_config[{{loop.index}}].bit_depth       = SaiHandle::Config::BitDepth::SAI_24BIT;
    sai_config[{{loop.index}}].a_sync          = SaiHandle::Config::Sync::{{codec.a_sync}};
    sai_config[{{loop.index}}].b_sync          = SaiHandle::Config::Sync::{{codec.b_sync}};
    sai_config[{{loop.index}}].a_dir           = SaiHandle::Config::Direction::{{codec.a_dir}};
    sai_config[{{loop.index}}].b_dir           = SaiHandle::Config::Direction::{{codec.b_dir}};
    sai_config[{{loop.index}}].pin_config.fs   = som.GetPin({{codec.pin.fs}});
    sai_config[{{loop.index}}].pin_config.mclk = som.GetPin({{codec.pin.mclk}});
    sai_config[{{loop.index}}].pin_config.sck  = som.GetPin({{codec.pin.sck}});
    sai_config[{{loop.index}}].pin_config.sa   = som.GetPin({{codec.pin.sa}});
    sai_config[{{loop.index}}].pin_config.sb   = som.GetPin({{codec.pin.sb}});
    {% endfor %}

    SaiHandle sai_handle[{{ 1 + external_codecs|length }}];
    sai_handle[0].Init(sai_config[0]);
    {% for codec in external_codecs %}
    sai_handle[{{loop.index}}].Init(sai_config[{{loop.index}}]);
    {% endfor %}

    dsy_gpio_pin codec_reset_pin = som.GetPin(29);
    Ak4556::Init(codec_reset_pin);

    AudioHandle::Config cfg;
    cfg.blocksize  = 48;
    cfg.samplerate = SaiHandle::Config::SampleRate::SAI_48KHZ;
    cfg.postgain   = 0.5f;
    som.audio_handle.Init(
      cfg, 
      sai_handle[0]
      {% for codec in external_codecs %}
      ,sai_handle[{{loop.index}}]
      {% endfor %}
    );
    {% endif %}

    {% if som == 'seed' %}
    som.adc.Start();
    {% endif %}
  }

  /** Handles all the controls processing that needs to occur at the block rate
   * 
   */
  void ProcessAllControls() 
  {
    {% if process != '' %} 
    {{ process }} 
    {% endif %}
    {% if som == 'patch_sm' %}
    som.ProcessAllControls();
    {% endif %}
  }

  /** Sets the audio sample rate
   *  \param sample_rate the new sample rate in Hz
   */
  void SetAudioSampleRate(size_t sample_rate) 
  {
    {% if som == 'seed' %}
    SaiHandle::Config::SampleRate enum_rate;
    if (sample_rate >= 96000)
      enum_rate = SAI_96KHZ;
    else if (sample_rate >= 48000)
      enum_rate = SAI_48KHZ;
    else if (sample_rate >= 32000)
      enum_rate = SAI_32KHZ;
    else if (sample_rate >= 16000)
      enum_rate = SAI_16KHZ;
    else
      enum_rate = SAI_8KHZ;
    som.SetAudioSampleRate(enum_rate);
    {% elif som == 'patch_sm' %}
    som.SetAudioSampleRate(sample_rate);
    {% endif %}
    {{samplerate}}
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
  inline void StartAudio(AudioHandle::AudioCallback cb)
  {
    som.StartAudio(cb);
  }

  /** This is the board's "System On Module"
   */
  {{som_class}} som;

  // I/O Components
  {{comps}}
  {{dispdec}}

};

} // namspace json2daisy

#endif // __JSON2DAISY_{{name|upper}}_H__