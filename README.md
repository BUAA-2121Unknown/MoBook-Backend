# MoBook-Backend

## Deployment

### Manual

Use daphne only. Simple, it is. Just run the following command in project root directory.

```bash
daphne -b 0.0.0.0 -p 5050 MoBook.asgi:application
```

### Auto

Step 1.

```bash
sudo cp zeta/daphne.service /etc/systemd/system/daphne.service

systemctl daemon-reload
systemctl start daphne.service
systemctl status daphne.service
```

Step 2.

```bash
sudo cp zeta/daphneservice.service /etc/systemd/system/daphneservice.service

systemctl daemon-reload
sudo systemctl start daphneservice
sudo systemctl enable daphneservice
ufw allow 5050
```

Step 3.

```bash
sudo shutdown -r now

systemctl status daphneservice.service
systemctl status daphne.service

```