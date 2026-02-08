/// Authentication service interface and implementation
abstract class IAuthService {
  Future<AuthResult> register(String email, String password, UserProfile profile);
  Future<AuthResult> login(String email, String password);
  Future<void> logout();
  Future<UserProfile> getProfile();
  Future<void> updateProfile(UserProfile profile);
}

class AuthResult {
  final bool success;
  final String? token;
  final String? error;
  
  AuthResult({required this.success, this.token, this.error});
}

class UserProfile {
  final String? id;
  final String email;
  final String firstName;
  final String lastName;
  
  UserProfile({
    this.id,
    required this.email,
    required this.firstName,
    required this.lastName,
  });
}

class AuthService implements IAuthService {
  @override
  Future<AuthResult> register(String email, String password, UserProfile profile) async {
    // To be implemented
    throw UnimplementedError();
  }

  @override
  Future<AuthResult> login(String email, String password) async {
    // To be implemented
    throw UnimplementedError();
  }

  @override
  Future<void> logout() async {
    // To be implemented
    throw UnimplementedError();
  }

  @override
  Future<UserProfile> getProfile() async {
    // To be implemented
    throw UnimplementedError();
  }

  @override
  Future<void> updateProfile(UserProfile profile) async {
    // To be implemented
    throw UnimplementedError();
  }
}
