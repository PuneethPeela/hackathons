import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

void main() {
  runApp(const PatientSupportApp());
}

class PatientSupportApp extends StatelessWidget {
  const PatientSupportApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        // Providers will be added here
      ],
      child: MaterialApp(
        title: 'Patient Support Assistant',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
          useMaterial3: true,
        ),
        home: const HomeScreen(),
      ),
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Patient Support Assistant'),
      ),
      body: const Center(
        child: Text('Welcome to Patient Support Assistant'),
      ),
    );
  }
}
