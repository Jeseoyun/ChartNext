from rest_framework import serializers
from .models import Company, UserInterest

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'ticker']

class UserInterestSerializer(serializers.ModelSerializer):
    company = CompanySerializer()

    class Meta:
        model = UserInterest
        fields = ['id', 'company', 'added_at']
        read_only_fields = ['id', 'added_at']

    def create(self, validated_data):
        company_data = validated_data.pop('company')
        company, created = Company.objects.get_or_create(**company_data)
        user_interest = UserInterest.objects.create(
            user=self.context['request'].user,
            company=company
        )
        return user_interest 