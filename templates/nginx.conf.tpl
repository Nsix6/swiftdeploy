events {}

http {
  log_format custom '$time_iso8601 | $status | $request_time s | $upstream_addr | $request';
  access_log /dev/stdout custom;

  server {
    listen 80;

    location / {
      proxy_pass http://app:{{app_port}};
      proxy_set_header Host $host;
      proxy_set_header Connection "";
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_read_timeout {{proxy_timeout}};
      proxy_pass_header X-Mode;
      add_header X-Deployed-By "{{x_deployed_by}}";
    }

    error_page 502 503 504 /error.json;

    location = /error.json {
      default_type application/json;
      return 502 '{"error":"{{error}}","code":"{{code}}","service":"{{service}}","contact":"{{contact}}"}';
    }
  }
}
