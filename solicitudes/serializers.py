from rest_framework import serializers
from .models import SolicitudCambio
from usuarios.serializers import UsuarioSerializer

class SolicitudCambioSerializer(serializers.ModelSerializer):
    solicitante_info = UsuarioSerializer(source='solicitante', read_only=True)
    resolutor_info = UsuarioSerializer(source='resolutor', read_only=True)

    class Meta:
        model = SolicitudCambio
        fields = '__all__'
        read_only_fields = ('fecha_solicitud', 'fecha_resolucion', 'resolutor', 'solicitante', 'estado')
    
    def create(self, validated_data):
        # Asignar solicitante automáticamente
        validated_data['solicitante'] = self.context['request'].user
        return super().create(validated_data)
