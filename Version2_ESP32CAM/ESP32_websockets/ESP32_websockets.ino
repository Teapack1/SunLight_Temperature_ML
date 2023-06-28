#include <ArduinoWebsockets.h>
#include <WiFi.h>

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
const char* websockets_server_host = "10.0.0.217"; //Enter server address
const uint16_t websockets_server_port = 8765; // Enter server port

using namespace websockets;

WebsocketsClient client;


void setup() {

    // Disable brownout detector
   WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
    setup_led();
      Serial.begin(115200);
    // Connect to wifi
    WiFi.begin(ssid, password);

    // Wait some time to connect to wifi
    for(int i = 0; i < 10 && WiFi.status() != WL_CONNECTED; i++) {
        Serial.print(".");
        delay(1000);
    }
    // Check if connected to wifi
    if(WiFi.status() != WL_CONNECTED) {
        Serial.println("No Wifi!");
        return;
    }

      // Initialize the camera
  Serial.print("Initializing the camera module...");
  configESPCamera();
  Serial.println("Camera OK!");


Serial.println("Connected to Wifi, Connecting to server.");
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
            Serial.println(control_value, 3);
              std::pair<int, int> brightnesses = led_controller(control_value);
              int warmBrightness = brightnesses.first;
              int coldBrightness = brightnesses.second;
              ledcWrite(warmPin, warmBrightness);
               ledcWrite(coldPin, coldBrightness);
                Serial.print("WarmW:");
                Serial.println(warmBrightness);
                Serial.print("ColdW:");
                Serial.println(coldBrightness);



              
            // Take a picture
            camera_fb_t * fb = esp_camera_fb_get();
            if(!fb) {
                Serial.println("Camera capture failed");
                return;
            } else {
             Serial.println("Image taken");
            }

              // Convert the image data to a base64 string
              String base64Image = base64::encode((const uint8_t*)fb->buf, fb->len);
              
              // Send the base64 image string over the WebSocket connection
              if(client.available()) {
                  client.send("image:" + base64Image);
                  Serial.println("Image sent to server.");
              }

        
            // Return the frame buffer back to the driver for reuse
            esp_camera_fb_return(fb);


            // Get RGBW values and send them over the WebSocket connection
            String rgbw_values = "1, 2, 3, 4"; //getRGBWValues();
            if(client.available()) {
                client.send("rgbw_values:" + rgbw_values);
                Serial.println("RGBW values sent to server.");
            }                
        }
    });
}

void loop() {
    // let the websockets client check for incoming messages
    if(client.available()) {
        client.poll();
    }

    delay(500);
}
