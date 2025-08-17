// Focus Assistant (with Active Buzzer) -- Arduino Mega
// HC-SR04 presence + RGB LED status + Active buzzer tones + Serial telemetry

// ---------- Pins ----------
#define TRIG   9
#define ECHO  10
#define LED_R  5
#define LED_G  6
#define LED_B  7
#define BUZZ   8   // ACTIVE buzzer: HIGH=beep, LOW=silent

// ---------- Tunables ----------
const int PRESENT_CM = 50;                 // seated if distance < this (calibrate)
const unsigned long SHORT_BREAK_S = 120;   // < 2 min away
const unsigned long WARNING_S     = 300;   // 2-5 min away; >5 => DISTRACTED

// Beep pacing (rate-limits)
const unsigned long WARNING_BEEP_PERIOD_MS    = 30000; // one beep every 30s
const unsigned long DISTRACTED_BEEP_PERIOD_MS = 30000; // triple-beep every 30s

// Flash timing
const unsigned long RED_FLASH_INTERVAL_MS = 250; // red flash ~2Hz

// ---------- State tracking ----------
unsigned long awayStart = 0;
unsigned long lastFlash = 0;
bool flashOn = false;

unsigned long lastWarnBeepAt = 0;
unsigned long lastDistractBeepAt = 0;

bool wasDistracted = false; // to trigger a single "back to focus" beep

// ---------- Helpers ----------
void setLED(bool r, bool g, bool b) {
  digitalWrite(LED_R, r ? HIGH : LOW);
  digitalWrite(LED_G, g ? HIGH : LOW);
  digitalWrite(LED_B, b ? HIGH : LOW);
}

// For ACTIVE buzzer, just drive HIGH/LOW for durations
void beepShort() {
  digitalWrite(BUZZ, HIGH);
  delay(90);
  digitalWrite(BUZZ, LOW);
}

void beepTriple() {
  for (int i=0; i<3; i++) {
    digitalWrite(BUZZ, HIGH); delay(70);
    digitalWrite(BUZZ, LOW);  delay(90);
  }
}

int readDistanceCM() {
  digitalWrite(TRIG, LOW); delayMicroseconds(2);
  digitalWrite(TRIG, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  unsigned long dur = pulseIn(ECHO, HIGH, 30000UL); // 30 ms timeout
  if (dur == 0) return 9999; // no echo
  return (int)(dur * 0.0343 / 2.0); // cm
}

void setup() {
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
  pinMode(LED_R, OUTPUT);
  pinMode(LED_G, OUTPUT);
  pinMode(LED_B, OUTPUT);
  pinMode(BUZZ, OUTPUT);
  digitalWrite(BUZZ, LOW);

  Serial.begin(9600);
  awayStart = millis();
}

void loop() {
  int d = readDistanceCM();
  unsigned long now = millis();

  bool present = (d < PRESENT_CM);

  if (present) {
    // Back to focus
    if (wasDistracted) {
      // Give one short confirmation beep when returning after a long absence
      beepShort();
      wasDistracted = false;
    }
    awayStart = now;                 // reset away timer
    setLED(false, true, false);      // GREEN
    Serial.println("FOCUS");
    // No periodic beep while focusing
  } else {
    unsigned long awayS = (now - awayStart) / 1000;

    if (awayS < SHORT_BREAK_S) {
      // Short, acceptable break
      setLED(false, true, false);    // GREEN
      Serial.println("SHORT BREAK");
    } else if (awayS < WARNING_S) {
      // Warning window
      setLED(false, false, true);    // BLUE
      Serial.println("WARNING");

      // Rate-limited single beep
      if (now - lastWarnBeepAt >= WARNING_BEEP_PERIOD_MS) {
        beepShort();
        lastWarnBeepAt = now;
      }
    } else {
      // Distracted: flashing red + triple beep every period
      if (now - lastDistractBeepAt >= DISTRACTED_BEEP_PERIOD_MS) {
        beepTriple();
        lastDistractBeepAt = now;
      }

      if (now - lastFlash >= RED_FLASH_INTERVAL_MS) {
        lastFlash = now;
        flashOn = !flashOn;
        setLED(flashOn, false, false); // RED flash
      }
      Serial.println("DISTRACTED");
      wasDistracted = true;
    }
  }

  delay(200); // loop ~5 Hz + blocking beeps (kept short)
}

/*
 * NOTES:
 * - If your RGB LED is COMMON ANODE, invert LED logic:
 *   Replace setLED(...) with:
 *     digitalWrite(LED_R, r ? LOW : HIGH);
 *     digitalWrite(LED_G, g ? LOW : HIGH);
 *     digitalWrite(LED_B, b ? LOW : HIGH);
 * - If you ever swap to a PASSIVE buzzer, use tone()/noTone() instead of HIGH/LOW.
 */
