services:
  app:
    image: {{app_image}}
    container_name: {{app_container}}
    environment:
      MODE: {{mode}}
      APP_PORT: {{app_port}}
      APP_VERSION: {{app_version}}
    volumes:
      - {{log_volume}}:/var/log/app
    restart: {{restart_policy}}
    networks:
      - {{network_name}}
    user: "1000:1000"
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    healthcheck:
      test:
        - CMD
        - curl
        - -f
        - http://localhost:{{app_port}}/healthz
      interval: 5s
      timeout: 2s
      retries: 5

  nginx:
    image: {{nginx_image}}
    container_name: {{nginx_container}}
    ports:
      - "{{nginx_port}}:80"
    depends_on:
      app:
        condition: service_healthy
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - {{log_volume}}:/var/log/nginx
    restart: {{restart_policy}}
    networks:
      - {{network_name}}

  opa:
    image: openpolicyagent/opa:latest
    container_name: swiftdeploy-opa
    command:
      - run
      - --server
      - /policies
    volumes:
      - ./policies:/policies
    networks:
      - {{network_name}}
    restart: unless-stopped

networks:
  {{network_name}}:
    driver: {{network_driver}}

volumes:
  {{log_volume}}:
