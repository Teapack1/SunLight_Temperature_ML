#include <utility>


void configESPCamera() {
  // Configure Camera parameters
 
  // Object to store the camera configuration parameters
  camera_config_t config;
 
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG; // Choices are YUV422, GRAYSCALE, RGB565, JPEG
 
  // Select LOWer framesize if the camera doesn't support PSRAM
  if (psramFound()) {
    config.frame_size = FRAMESIZE_VGA; // FRAMESIZE_ + QVGA|CIF|VGA|SVGA|XGA|SXGA|UXGA
    config.jpeg_quality = 6; //10-63 LOWer number means LOWer quality
    config.fb_count = 1;
  } else {
    config.frame_size = FRAMESIZE_QVGA;
    config.jpeg_quality = 6;
    config.fb_count = 1;
  }
 
  // Initialize the Camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
 
  // Camera quality adjustments
  sensor_t * s = esp_camera_sensor_get();
 
  s->set_brightness(s, 0);     // -2 to 2
  s->set_contrast(s, 0);       // -2 to 2
  s->set_saturation(s, 0);     // -2 to 2
  s->set_special_effect(s, 0); // 0 to 6 (0 - No Effect, 1 - Negative, 2 - Grayscale, 3 - Red Tint, 4 - Green Tint, 5 - Blue Tint, 6 - Sepia)
  s->set_whitebal(s, 0);       // 0 = disable , 1 = enable
  s->set_awb_gain(s, 0);       // 0 = disable , 1 = enable
  s->set_wb_mode(s, 0);        // 0 to 4 - if awb_gain enabled (0 - Auto, 1 - Sunny, 2 - Cloudy, 3 - Office, 4 - Home)
  s->set_exposure_ctrl(s, 0);  // 0 = disable , 1 = enable
  s->set_aec2(s, 1);           // 0 = disable , 1 = enable
  s->set_ae_level(s, 0);       // -2 to 2
  s->set_aec_value(s, 10);    // 0 to 1200
  s->set_gain_ctrl(s, 0);      // 0 = disable , 1 = enable
  s->set_agc_gain(s, 0);       // 0 to 30
  s->set_gainceiling(s, (gainceiling_t)0);  // 0 to 6
  s->set_bpc(s, 0);            // 0 = disable , 1 = enable
  s->set_wpc(s, 0);            // 0 = disable , 1 = enable
  s->set_raw_gma(s, 0);        // 0 = disable , 1 = enable
  s->set_lenc(s, 0);           // 0 = disable , 1 = enable
  s->set_hmirror(s, 0);        // 0 = disable , 1 = enable
  s->set_vflip(s, 0);          // 0 = disable , 1 = enable
  s->set_dcw(s, 0);            // 0 = disable , 1 = enable
  s->set_colorbar(s, 0);       // 0 = disable , 1 = enable
}


std::pair<int, int> led_controller(float controlValue){
      int warmBrightness, coldBrightness;
       
      if (controlValue <= 0.5) {
      warmBrightness = 255;
      coldBrightness = int((controlValue * 2) * 255); // Map control value for Cold LED (0 to 0.5 -> 0 to 255)
    } else {
      warmBrightness = int((1 - (controlValue - 0.5) * 2) * 255); // Map control value for Warm LED (0.5 to 1 -> 255 to 0)
      coldBrightness = 255;
    }
    return std::make_pair(warmBrightness, coldBrightness);
}



void setup_led(){
    // Setup channel 0
    ledcSetup(LEDC_CHANNEL_1, LEDC_BASE_FREQ, LEDC_TIMER_8_BIT);
    ledcAttachPin(warmPin, LEDC_CHANNEL_1);

    // Setup channel 1
    ledcSetup(LEDC_CHANNEL_2, LEDC_BASE_FREQ, LEDC_TIMER_8_BIT);
    ledcAttachPin(coldPin, LEDC_CHANNEL_2);
}

void create_ap(bool AP, const char* ssid, const char* pass, Adafruit_SSD1306& display){

  if (AP == true){


    Serial.println("Setting up AP...");
    WiFi.softAP(ssid, pass);
    
    IPAddress IP = WiFi.softAPIP();
    
    Serial.println("AP setup succesfully!");
    Serial.println("");
    Serial.print("AP IP address: ");
    Serial.println(IP);

        display.clearDisplay();
        display.setTextSize(1);
        display.setCursor(0, 0);
        display.println("AP setup successfully!");
        display.println("");
        display.print("AP IP address: ");
        display.println(IP);
        display.display();
    delay(500);
    
} else if (AP == false){
        display.clearDisplay();
        display.setTextSize(1);   
      display.setCursor(0, 0);
        display.setTextColor(BLACK, WHITE);
     display.println(F("connecting to AP..."));
    display.display();
     
    WiFi.begin(ssid, pass);
    uint8_t idx = 0;
    while (WiFi.status() != WL_CONNECTED){
            if (idx<max(display.width(),display.height())/2){
        idx+=2;
      display.drawCircle(display.width()/2, display.height()/2, idx, SSD1306_WHITE);
      display.display();
      delay(1);
      
      } else if (idx>max(display.width(),display.height())/2){
        idx-=2;
      display.drawCircle(display.width()/2, display.height()/2, idx, SSD1306_WHITE);
      display.display();
      delay(1);
      }
      
      delay(1000);     
      Serial.print(".");
       
   }
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("Local IP address: ");
    Serial.println(WiFi.localIP());

      for(uint8_t i=idx; i<max(display.width(),display.height())/2; i+=2) {
        display.drawCircle(display.width()/2, display.height()/2, i, SSD1306_WHITE);
        display.display();
        delay(1);
        idx = i;
      }

      for(uint8_t i=idx; i>0; i-=2) {
      display.drawCircle(display.width()/2, display.height()/2, i, SSD1306_BLACK);
      display.display();
      delay(1);
    }
    
        display.clearDisplay();
        display.setTextSize(1);   
      display.setCursor(0, 0);
        display.setTextColor(WHITE);
     display.println(F("WiFi Connected!"));
     display.println(WiFi.localIP());
    display.display();
    delay(2000);   
 }
}

void print_colors(int ct, int l, int r, int g, int b, int c){
    Serial.print("Color Temp: "); Serial.print(ct, DEC); Serial.print(" K - ");
    Serial.print("Lux: "); Serial.print(l, DEC); Serial.print(" - ");
    Serial.print("R: "); Serial.print(r, DEC); Serial.print(" ");
    Serial.print("G: "); Serial.print(g, DEC); Serial.print(" ");
    Serial.print("B: "); Serial.print(b, DEC); Serial.print(" ");
    Serial.print("C: "); Serial.print(c, DEC); Serial.print(" ");
    Serial.println(" ");
}

char* ip_setup(Adafruit_SSD1306& display, const int touchPin, const int longPressTime, const int acceptTime, const char* ip_prefix) {

unsigned long lastBlinkTime = 0;
unsigned long lastChangeTime = 0;
int currentDigit = 0;
bool blinkState = false;
int digits[4] = {0, -1, -1, -1}; 

static char websockets_server_host[16];

int lastTouchState = LOW;
  while (true) {
    int touchState = digitalRead(touchPin);
    if (touchState == HIGH && lastTouchState == LOW) {
      lastChangeTime = millis();
      digits[currentDigit]++;
      if (digits[currentDigit] > 9) {
        digits[currentDigit] = -1;
      }
    }
    else if (touchState == HIGH && (millis() - lastChangeTime >= longPressTime)) {
      lastChangeTime = millis();
      currentDigit++;
      if (currentDigit > 3) {
        currentDigit = 0;
      }
    }
    else if (millis() - lastChangeTime >= acceptTime) {
      if (digits[1] == -1) {
        sprintf(websockets_server_host, "%s%d", ip_prefix, digits[0]);
      } else if (digits[2] == -1) {
        sprintf(websockets_server_host, "%s%d%d", ip_prefix, digits[0], digits[1]);
      } else {
        sprintf(websockets_server_host, "%s%d%d%d", ip_prefix, digits[0], digits[1], digits[2]);
      }
      // websockets_server_host now contains the IP address
      break;
    }

    // Display the current IP address on the screen
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);
    display.println("Server IP:");
    display.print(ip_prefix);
    for (int i = 0; i < 3; i++) {
      if (i == currentDigit && blinkState) {
        display.print(" ");
      } else if (digits[i] == -1) {
        display.print(" ");
      } else {
        display.print(digits[i]);
      }
    }
    display.display();

    // Toggle blinkState every 500ms
    if (millis() - lastBlinkTime >= 500) {
      blinkState = !blinkState;
      lastBlinkTime = millis();
    }

    lastTouchState = touchState;
  }
  return websockets_server_host;
}
