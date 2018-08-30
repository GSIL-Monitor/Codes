supervisorctl stop tyc_crack
killall chromedriver-linux
killall chrome
killall Xvfb
rm -rf /tmp/.com.google.Chrome.*
rm -rf /tmp/.org.chromium.Chromium.*
supervisorctl start tyc_crack