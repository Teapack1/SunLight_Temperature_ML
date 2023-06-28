//Pins
#define LEDC_CHANNEL_0     LEDC_CHANNEL_0
#define LEDC_CHANNEL_1     LEDC_CHANNEL_1
#define LEDC_TIMER_13_BIT  13
#define LEDC_BASE_FREQ     5000
#define warmPin 2
#define coldPin 4

void setup_led(){
    // Setup channel 0
    ledcSetup(LEDC_CHANNEL_0, LEDC_BASE_FREQ, LEDC_TIMER_13_BIT);
    ledcAttachPin(warmPin, LEDC_CHANNEL_0);

    // Setup channel 1
    ledcSetup(LEDC_CHANNEL_1, LEDC_BASE_FREQ, LEDC_TIMER_13_BIT);
    ledcAttachPin(coldPin, LEDC_CHANNEL_1);
}

//Camera
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22
