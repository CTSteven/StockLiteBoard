from rest_framework import serializers

class StockPriceSerializer(serializers.Serializer):
    # 'Open','High','Low','Close','Volume']]
    open = serializers.FloatField()
    high = serializers.FloatField()
    low = serializers.FloatField()
    close = serializers.FloatField()
    volume = serializers.IntegerField()