import 'dart:io';

/// Lab report service interface and implementation
abstract class ILabReportService {
  Future<UploadResult> uploadReport(File file);
  Future<LabAnalysis> getAnalysis(String reportId);
  Future<List<LabReport>> getReportHistory();
}

class UploadResult {
  final String reportId;
  final String status;
  final String message;
  
  UploadResult({
    required this.reportId,
    required this.status,
    required this.message,
  });
}

class LabAnalysis {
  final String reportId;
  final DateTime reportDate;
  final List<LabValue> results;
  final String overallSummary;
  final List<String> preventiveSuggestions;
  
  LabAnalysis({
    required this.reportId,
    required this.reportDate,
    required this.results,
    required this.overallSummary,
    required this.preventiveSuggestions,
  });
}

class LabValue {
  final String testName;
  final double value;
  final String unit;
  final String referenceRange;
  final String status;
  final String interpretation;
  
  LabValue({
    required this.testName,
    required this.value,
    required this.unit,
    required this.referenceRange,
    required this.status,
    required this.interpretation,
  });
}

class LabReport {
  final String id;
  final String fileName;
  final DateTime uploadDate;
  final String status;
  
  LabReport({
    required this.id,
    required this.fileName,
    required this.uploadDate,
    required this.status,
  });
}

class LabReportService implements ILabReportService {
  @override
  Future<UploadResult> uploadReport(File file) async {
    // To be implemented
    throw UnimplementedError();
  }

  @override
  Future<LabAnalysis> getAnalysis(String reportId) async {
    // To be implemented
    throw UnimplementedError();
  }

  @override
  Future<List<LabReport>> getReportHistory() async {
    // To be implemented
    throw UnimplementedError();
  }
}
