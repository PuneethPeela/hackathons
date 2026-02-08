/// Medication management service interface and implementation
abstract class IMedicationService {
  Future<Medication> addMedication(MedicationDetails details);
  Future<void> updateMedication(String id, MedicationDetails details);
  Future<void> recordAdherence(String medicationId, DateTime timestamp);
  Future<AdherenceReport> getAdherenceReport(String medicationId);
}

class Medication {
  final String id;
  final String name;
  final String dosage;
  final String frequency;
  final List<String> scheduleTimes;
  
  Medication({
    required this.id,
    required this.name,
    required this.dosage,
    required this.frequency,
    required this.scheduleTimes,
  });
}

class MedicationDetails {
  final String name;
  final String dosage;
  final String frequency;
  final List<String> scheduleTimes;
  final String? instructions;
  
  MedicationDetails({
    required this.name,
    required this.dosage,
    required this.frequency,
    required this.scheduleTimes,
    this.instructions,
  });
}

class AdherenceReport {
  final double adherenceScore;
  final int totalDoses;
  final int takenDoses;
  final int missedDoses;
  
  AdherenceReport({
    required this.adherenceScore,
    required this.totalDoses,
    required this.takenDoses,
    required this.missedDoses,
  });
}

class MedicationService implements IMedicationService {
  @override
  Future<Medication> addMedication(MedicationDetails details) async {
    // To be implemented
    throw UnimplementedError();
  }

  @override
  Future<void> updateMedication(String id, MedicationDetails details) async {
    // To be implemented
    throw UnimplementedError();
  }

  @override
  Future<void> recordAdherence(String medicationId, DateTime timestamp) async {
    // To be implemented
    throw UnimplementedError();
  }

  @override
  Future<AdherenceReport> getAdherenceReport(String medicationId) async {
    // To be implemented
    throw UnimplementedError();
  }
}
