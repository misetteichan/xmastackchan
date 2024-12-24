// Copyright (c) 2024 misetteichan
// Licensed under the MIT License. See LICENSE file for details.

#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#include <vector>
#include <algorithm>
#include <random>

class Scene {
  const unsigned long _duration;
 public:
  explicit Scene(unsigned long duration) : _duration(duration) {}
  void run(Adafruit_NeoPixel& strip) {
    enter(strip);
    const auto t1 = millis();
    body(strip);
    const auto t2 = millis();
    if (t2 - t1 < _duration) {
      delay(_duration - (t2 - t1));
    }
    exit(strip);
  }
 protected:
  virtual void enter(Adafruit_NeoPixel&) {}
  virtual void body(Adafruit_NeoPixel&) {}
  virtual void exit(Adafruit_NeoPixel&) {}

  static uint32_t HSV(int h, int s, int v) {
    return Adafruit_NeoPixel::gamma32(Adafruit_NeoPixel::ColorHSV(h*65535/100, s, v));
  }
};

class YellowFade : public Scene {
 public:
  YellowFade(unsigned long duration, uint16_t no, uint32_t wait, int steps)
  : Scene(duration), _no(no), _wait(wait), _steps(steps) {}
 protected:
  void body(Adafruit_NeoPixel& strip) override { 
    for (auto v = 0; v < 255; v += _steps) {
      strip.setPixelColor(_no, HSV(16, 255, v));
      strip.show();
      delay(_wait);
    }
  } 
 private:
  const uint16_t _no;
  const uint32_t _wait;
  const int _steps;
};

class YellowBlink : public Scene {
  const int _repeat; 
 public:
  YellowBlink(int repeat) : Scene(0), _repeat(repeat) {}
 protected:
  void body(Adafruit_NeoPixel& strip) override { 
    for (auto n = 0; n < _repeat; ++n) {
      fadeout(strip);
      fadein(strip);
      delay(1000);
    }
    fadeout(strip);
  }
 private:
  static void fadein(Adafruit_NeoPixel& strip) {
    for (auto v = 0; v < 255; ++v) {
      strip.fill(HSV(16, 255, v), 1);
      strip.show();
      delay(5);
    }
  }
  static void fadeout(Adafruit_NeoPixel& strip) {
    for (auto v = 0; v < 255; ++v) {
      strip.fill(HSV(16, 255, 255 - v), 1);
      strip.show();
      delay(5);
    }
  }
};

class RandomBlink : public Scene {
  const int _repeat; 
 public:
  RandomBlink(int repeat) : Scene(0), _repeat(repeat) {}
 protected:
  void body(Adafruit_NeoPixel& strip) override {
    std::random_device rd;
    std::mt19937 g(rd());

    std::vector<int> hue = { 0, 33, 66 };
    std::vector<int> prev = hue;
    const auto steps = _repeat > 0 ? 1 : 0;
    for (auto n = _repeat - steps; n >= 0; n -= steps) {
      do {
        // 絶対に前回と違う色にするマン
        std::shuffle(hue.begin(), hue.end(), g);
      } while(!check(hue, prev));
      blink(strip, hue);
      prev = hue;
    }
  }
 private:
  static bool check(const std::vector<int>& v1, const std::vector<int>& v2) {
    for (auto n = 0; n < v1.size(); ++n) {
      if (v1[n] == v2[n]) {
        return false;
      }
    }
    return true;
  }

  static void blink(Adafruit_NeoPixel& strip, const std::vector<int>& hue) {
    for (auto v = 0; v < 255; ++v) {
      for (auto n = 0; n < 3; ++n) {
        strip.setPixelColor(n + 1, HSV(hue[n], 255, v));
      }
      strip.show();
      delay(5);
    }
    delay(500);
    for (auto v = 0; v < 255; ++v) {
      for (auto n = 0; n < 3; ++n) {
        strip.setPixelColor(n + 1, HSV(hue[n], 255, 255 - v));
      }
      strip.show();
      delay(5);
    }
  }
};

class Gaming : public Scene {
 public:
  Gaming() : Scene(0) {}
 protected:
  void body(Adafruit_NeoPixel& strip) override { 
    while (true) {
      rainbow(strip, 3);
    }
  }
  private:
   static void rainbow(Adafruit_NeoPixel& strip, int wait) {
    for (auto h = 0; h < 5*65536; h += 256) {
      strip.rainbow(h);
      strip.show();
      delay(wait);
    }
   }
};

class NeoPixels {
  Adafruit_NeoPixel _strip;
  std::vector<Scene*> _scenes;
 public:
  NeoPixels(int pin) : _strip(4, pin, NEO_RGB + NEO_KHZ800) {
#if 0
    _scenes.emplace_back(new Gaming());
#else
    _scenes.emplace_back(new YellowFade(6000, 0, 10, 1));
    for (auto n = 1; n < _strip.numPixels(); ++n) {
      _scenes.emplace_back(new YellowFade(1000, n, 5, 5));
    }
    _scenes.emplace_back(new YellowBlink(2));
    _scenes.emplace_back(new RandomBlink(0));
#endif
  }

  void begin() {
    _strip.begin();
    _strip.show();
  }

  void loop() {
    for (auto& scene : _scenes) {
      scene->run(_strip);
    }
    while (true) {
      delay(1000);
    }
  }
};

NeoPixels* neopixels = nullptr;

void setup() {
  neopixels = new NeoPixels(25);
  neopixels->begin();
}

void loop() {
  neopixels->loop();
}
