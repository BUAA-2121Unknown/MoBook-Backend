# MoBook-Backend
## Deployment

Use daphne only. Simple, it is. Just run the following command in project root directory.

```bash
daphne -b 0.0.0.0 -p 5050 MoBook.asgi:application
```