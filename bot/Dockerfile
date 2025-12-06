FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
ENV BOT_TOKEN=YOUR_BOT_TOKEN
ENV BOT_2_TOKEN=YOUR_ADMIN_BOT_TOKEN
ENV ADMIN_CHAT_ID=YOUR_ADMIN_CHAT_ID
ENV BOT_2_ADMIN_CHAT_ID=YOUR_ADMIN_CHAT_ID
ENV BACKEND_API_URL=https://your-public-backend.com/api/v1/save_order
ENV ABA_PAY_LINK=https://pay.ababank.com/oRF8/2ug5pzi4
CMD ["python", "main.py"]
