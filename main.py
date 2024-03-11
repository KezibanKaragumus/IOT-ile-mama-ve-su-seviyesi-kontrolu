from machine import Pin, ADC, time_pulse_us
from time import sleep
import utime
import socket
import network
import urequests

wifiSSID = '------'
wifiPassword = '---------'

def baglantiYap():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    if not wifi.isconnected():
        print('baglanıyor')
        wifi.connect(wifiSSID, wifiPassword)
        while not wifi.isconnected():
            pass
    print('Ag ayarları', wifi.ifconfig())

baglantiYap()

adc_pin = 34
trigger_pin = Pin(4, Pin.OUT)
echo_pin = Pin(5, Pin.IN)

adc = ADC(Pin(adc_pin))
adc.width(ADC.WIDTH_12BIT)
adc.atten(ADC.ATTN_11DB)

def measure_water_level(samples=1): #degerleri  defa okutup ortalamasını aldık
    total_measurements = 0
    for _ in range(samples):
        adcDegeri = adc.read()
        milliVolt = adcDegeri * (5000 / 4096)
        water_level = milliVolt / 10
        water_level = (water_level / 5)# 5e bölmemizin nedeni en fazla 500 degerini alıyorduk yüzdeye çevirdik.
        if water_level > 100:
            water_level = 100
        if water_level < 0:
            water_level = 0
        total_measurements += water_level
    return total_measurements / samples

def kontrol_et(samples=1):
    total_measurements = 0
    for _ in range(samples):
        trigger_pin.off()
        utime.sleep_us(2)
        trigger_pin.on()
        utime.sleep_us(5)
        trigger_pin.off()
        pulse_time = time_pulse_us(echo_pin, 1, 30000)
        distance_cm = (pulse_time / 2) / 29.1
        a = (25 - distance_cm) * 4 #kabımın boyu yaklaşık 25cm bundan dolayı içindeki mama seviyesini bulmak için 25ten çıkarıyoruz. 4 ile çarpmamın nedeni ise yaklaşık degeri 100 üzerinden görmek
        if a < 0:
            a = 0
        if a > 100:
            a = 100
        total_measurements += a
    return total_measurements / samples

def tumDegerleriOku():
    Su = measure_water_level()
    Mama = kontrol_et()
    return Su, Mama

httpBaslik = {'Content-Type': 'application/json'}
thingSpeakApiKey = '---------------'

while True:
    Su, Mama = tumDegerleriOku()
    print('Su_seviyesi', Su)
    print('Mama_seviyesi', Mama)

    sensorDegerleri = {'field2': Su, 'field1': Mama}

    request = urequests.post('http://api.thingspeak.com/update?api_key=' + thingSpeakApiKey,
                             json=sensorDegerleri, headers=httpBaslik)

    request.close()
    sleep(1)

