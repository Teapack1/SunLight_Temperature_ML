#include <ArduinoWebsockets.h>
#include <WiFi.h>
#include <Wire.h>
#include "Adafruit_TCS34725.h"

// Camera libraries
#include <base64.h>
#include "esp_camera.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include "driver/rtc_io.h"
#include "camera_pins.h"
#include "functions.h"

 // Counter for picture number
unsigned int pictureCount = 0;

const char* ssid = "Major"; //Enter SSID
const char* password = "12345ABCDE"; //Enter Password
const char* websockets_server_host = "10.0.0.221"; //Enter server address
const uint16_t websockets_server_port = 8765; // Enter server port

using namespace websockets;
WebsocketsClient client;
TwoWire I2CSensors = TwoWire(0);
Adafruit_TCS34725 tcs = Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_300MS, TCS34725_GAIN_1X);


void connect_server(const char* websockets_server_host, const uint16_t websockets_server_port){
    Serial.println("Connecting to Websocket server.");
    // try to connect to Websockets server
    bool connected = false;
    while (!connected) {
        connected = client.connect(websockets_server_host, websockets_server_port, "/");
        if(connected) {
            Serial.println("Connected!");
        } else {
            Serial.println("Not Connected!");
            delay(1000); // Wait for a second before trying to connect again
        }
    }
}


void setup() {
  
    pinMode(TCS34725_LED_PIN, OUTPUT);
    digitalWrite(TCS34725_LED_PIN, LOW);
    
    // Disable brownout detector
   WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
    setup_led();
      Serial.begin(115200);
     I2CSensors.begin(I2C_SDA, I2C_SCL);
     
  create_ap(false, ssid, password);

      // Initialize the camera
  Serial.print("Initializing the camera module...");
  configESPCamera();
  Serial.println("Camera OK!");

  // Initialize the RGB sensor
    if (tcs.begin()) {
    Serial.println("Color sensor OK!");
  } else {
    Serial.println("No TCS34725 found ... check your connections");
    while (1);
  }


    // -------------------WEBSOCKET CALLBACK------------------------
    // This block of code is setting up a callback function that will be executed whenever a message is received from the WebSocket server.
      client.onMessage([&](WebsocketsMessage message){
          Serial.print("Got Message: ");
          Serial.println(message.data());
          String message_type, data;
          int separatorIndex = message.data().indexOf(':');
          if (separatorIndex != -1) {
              message_type = message.data().substring(0, separatorIndex);
              data = message.data().substring(separatorIndex + 1);
          }
  
      // If control_value recieved, setup the LED output
          if (message_type == "control_value") {
              // Handle control value here
              float control_value = data.toFloat();
                std::pair<int, int> brightnesses = led_controller(control_value);
                int warmBrightness = brightnesses.first;
                int coldBrightness = brightnesses.second;
                ledcWrite(warmPin, warmBrightness);
                 ledcWrite(coldPin, coldBrightness);
                  Serial.print("Warm White level: ");
                  Serial.println(warmBrightness);
                  Serial.print("Cold White level: ");
                  Serial.println(coldBrightness);
                  
                   Serial.println("DIMMING THE LEDs!");
                   delay(300);
                      
                        // Take a picture
                        camera_fb_t * fb = esp_camera_fb_get();
                        if(!fb) {
                            Serial.println("Camera capture failed");
                            return;
                        } else {
                         Serial.println("Image taken.");
                        }
            
                          // Convert the image data to a base64 string
                          String base64Image = base64::encode((const uint8_t*)fb->buf, fb->len);
                          
                          // Send the base64 image string over the WebSocket connection
                          if(client.available()) {
                              client.send("image:" + base64Image);
                              Serial.println("Image sent to the server.");
                          }
                           esp_camera_fb_return(fb);
                        
                        // Get RGBW values and send them over the WebSocket connection
                        uint16_t r, g, b, c, colorTemp, lux;
                        tcs.getRawData(&r, &g, &b, &c);
                        Serial.println("Color data read.");
                          colorTemp = tcs.calculateColorTemperature_dn40(r, g, b, c);
                          lux = tcs.calculateLux(r, g, b);
                        Serial.println("Light props calculated.");
                            
                          //  print_colors(colorTemp, lux, r, g, b, c); // output of the sensor

                        if(client.available()) {
                            String rgbw_values = String(r) + "," + String(g) + "," + String(b) + "," + String(c);
                            client.send("rgbw_values:" + rgbw_values);
                            String light_specs = String(colorTemp) + "," + String(lux);
                            client.send("light_specs:" + light_specs);
                            Serial.println("color data sent to the server.");
                        }
                  
                  Serial.println("----------END--OF--THE--CALL----------");       
                  Serial.println(""); 
                    }
                });

         //--------------WEBSOCKET EVENTS----------------
         
          client.onEvent([](WebsocketsEvent event, String data) {
              if(event == WebsocketsEvent::ConnectionOpened) {
                  Serial.println("Connnection Opened");
              } else if(event == WebsocketsEvent::ConnectionClosed) {
                  Serial.println("Connnection Closed");
              } else if(event == WebsocketsEvent::GotPing) {
                  Serial.println("Got a Ping!");
              } else if(event == WebsocketsEvent::GotPong) {
                  Serial.println("Got a Pong!");
              }
          });

        connect_server(websockets_server_host, websockets_server_port);
    

}


void loop() {
    // let the websockets client check for incoming messages
    if(client.available()) {
        client.poll();
       delay(100);
    } else {
      connect_server(websockets_server_host, websockets_server_port);
       delay(100);
    }
   
}
