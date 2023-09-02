# MoBook-Backend

## Deployment

### Daphne

Use daphne only. Simple, it is. Just run the following command in project root directory.

```bash
daphne -b 0.0.0.0 -p 5050 MoBook.asgi:application
```

### Nginx

```bash
sudo vim /etc/nginx/conf.d/default.conf
```

And write configurations like this.

```
server {
        listen 80;
        server_name 81.70.161.76;
        
        location /media {
                alias /home/ubuntu/workspace//media/;
                autoindex on;
        }
}
```

Finally, reload configurations.

```bash
sudo nginx -s reload
```