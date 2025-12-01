-- Миграция: Добавление полей для баллов в таблицу delivery_orders
-- Выполните этот скрипт в вашей базе данных PostgreSQL

ALTER TABLE delivery_orders 
ADD COLUMN IF NOT EXISTS points_used INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS points_awarded INTEGER DEFAULT 0;

-- Комментарии к полям
COMMENT ON COLUMN delivery_orders.points_used IS 'Количество списанных баллов при оформлении заказа';
COMMENT ON COLUMN delivery_orders.points_awarded IS 'Количество начисленных баллов при выполнении заказа';

