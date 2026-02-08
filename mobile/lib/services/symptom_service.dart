/// Symptom checker service interface and implementation
abstract class ISymptomService {
  Future<List<String>> searchSymptoms(String query);
  Future<SymptomAnalysis> analyzeSymptoms(List<String> symptoms);
  Future<List<Disease>> getPossibleConditions(SymptomAnalysis analysis);
}

class SymptomAnalysis {
  final String id;
  final List<String> symptoms;
  final String riskSeverity;
  final List<Disease> predictions;
  
  SymptomAnalysis({
    required this.id,
    required this.symptoms,
    required this.riskSeverity,
    required this.predictions,
  });
}

class Disease {
  final String name;
  final double confidence;
  final String description;
  
  Disease({
    required this.name,
    required this.confidence,
    required this.description,
  });
}

class SymptomService implements ISymptomService {
  @override
  Future<List<String>> searchSymptoms(String query) async {
    // To be implemented
    throw UnimplementedError();
  }

  @override
  Future<SymptomAnalysis> analyzeSymptoms(List<String> symptoms) async {
    // To be implemented
    throw UnimplementedError();
  }

  @override
  Future<List<Disease>> getPossibleConditions(SymptomAnalysis analysis) async {
    // To be implemented
    throw UnimplementedError();
  }
}
