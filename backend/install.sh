sudo cp ./meiri.nginx /etc/nginx/sites-available/meiri
cd /etc/nginx/sites-enabled/
sudo ln -s ../sites-available/meiri meiri
sudo systemctl restart nginx.service
