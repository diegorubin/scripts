require 'bunny'
require 'byebug'
require 'json'

module RabbitMQ
  class Consumer
    def initialize(queue_name)
      @connection = Bunny.new
      @connection.start

      channel = @connection.create_channel
      @queue = channel.queue(queue_name, durable: true)
    end

    def on_consume
      @queue.subscribe(block: true) do |_delivery_info, properties, body|
        yield(body, properties)
      end
    end

    def close
      @connection.close
    end
  end
end

queue = ARGV[0]

consumer = RabbitMQ::Consumer.new(queue)
consumer.on_consume do |body, properties|
  destination = File.open("#{queue}.json", 'a')
  destination.puts({ 'body' => body, 'headers' => properties[:headers].to_json }.to_json)
  destination.close
end

