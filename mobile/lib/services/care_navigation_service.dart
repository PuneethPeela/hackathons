/// Care navigation service interface and implementation
abstract class ICareNavigationService {
  Future<Appointment> scheduleAppointment(AppointmentDetails details);
  Future<List<Appointment>> getAppointments();
  Future<TreatmentProgress> getProgress();
  Future<void> updateProgress(String milestoneId, bool completed);
}

class Appointment {
  final String id;
  final String title;
  final String? description;
  final DateTime appointmentDate;
  final String? location;
  final String? doctorName;
  final String status;
  
  Appointment({
    required this.id,
    required this.title,
    this.description,
    required this.appointmentDate,
    this.location,
    this.doctorName,
    required this.status,
  });
}

class AppointmentDetails {
  final String title;
  final String? description;
  final DateTime appointmentDate;
  final String? location;
  final String? doctorName;
  final String? specialty;
  
  AppointmentDetails({
    required this.title,
    this.description,
    required this.appointmentDate,
    this.location,
    this.doctorName,
    this.specialty,
  });
}

class TreatmentProgress {
  final List<Milestone> milestones;
  final double completionPercentage;
  
  TreatmentProgress({
    required this.milestones,
    required this.completionPercentage,
  });
}

class Milestone {
  final String id;
  final String title;
  final bool completed;
  final DateTime? completedDate;
  
  Milestone({
    required this.id,
    required this.title,
    required this.completed,
    this.completedDate,
  });
}

class CareNavigationService implements ICareNavigationService {
  @override
  Future<Appointment> scheduleAppointment(AppointmentDetails details) async {
    // To be implemented
    throw UnimplementedError();
  }

  @override
  Future<List<Appointment>> getAppointments() async {
    // To be implemented
    throw UnimplementedError();
  }

  @override
  Future<TreatmentProgress> getProgress() async {
    // To be implemented
    throw UnimplementedError();
  }

  @override
  Future<void> updateProgress(String milestoneId, bool completed) async {
    // To be implemented
    throw UnimplementedError();
  }
}
