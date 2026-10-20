# Clinic Management API

## 1. Project Overview

The Clinic Management API is a backend system designed to manage the core operations of a single clinic. It will support patient registration, appointment scheduling, staff management, authentication, and medical record management.

The system will provide separate access for clinic staff and patients. Patients will be able to manage their appointments and view their finalized medical records, while authorized clinic staff will manage patient information, appointments, and clinical documentation according to their responsibilities.

The API will be developed as a portfolio project using fictional patient data.

## 2. Project Objectives

The objectives are to:

* Digitize patient registration and appointment management.

* Provide secure authentication and role-based access control.

* Allow patients to access their appointments and medical records.

* Enable clinic staff to manage appointments and patient information.

* Maintain accurate, traceable medical records.

* Protect patient information and support privacy-conscious data handling.

* Demonstrate sound backend engineering practices, including database design, validation, testing, and API documentation.

## 3. Technology Stack

* **Programming language:** Python

* **Backend framework:** FastAPI

* **Database:** PostgreSQL

* **ORM:** SQLAlchemy 2.0

* **Database migrations:** Alembic

* **Authentication:** JWT access tokens and server-side refresh-token storage

* **API documentation:** FastAPI-generated OpenAPI documentation

## 4. System Users and Roles

### 4.1 Administrator

The administrator will be responsible for managing the system and its staff accounts.

Responsibilities:

* Manage staff accounts.

* Assign staff roles.

* Manage clinic departments.

* Control staff account access.

### 4.2 Receptionist

The receptionist will manage patient registration and appointment administration.

Responsibilities:

* Register new patients.

* Create patient records before account activation.

* Issue patient registration codes.

* Book and manage appointments.

* Assign doctors to appointments.

* Update appointment statuses according to authorized workflows.

### 4.3 Doctor

Doctors will manage consultations and clinical documentation.

Responsibilities:

* View appointments assigned to them.

* Access patient information necessary for their duties.

* Create medical reports.

* Save reports as drafts.

* Finalize medical reports.

* View relevant patient medical history.

A finalized medical report must not be directly editable. Corrections must follow a traceable process that preserves the original report.

### 4.4 Nurse

Nurses will have a separate staff role.

Planned responsibilities include:

* Access relevant patient information.

* View relevant appointments.

* Record patient vital signs and nursing observations.

* Access information necessary for their assigned duties.

Nurse-specific functionality will be implemented in a later development phase.

### 4.5 Patient

Patients will have access to their own accounts and information.

Responsibilities:

* Activate an account using a registration code issued by the clinic.

* Log in securely.

* Book appointments by selecting an eligible department and date.

* View their appointments and assigned doctors.

* View their finalized medical records.

* View their relevant medical history.

Patients must not be able to edit their medical records or access another patient's private information.

## 5. Functional Requirements

### 5.1 Authentication and Authorization

The system shall:

* Allow authorized staff to access their accounts.

* Allow registered patients to activate their accounts and log in.

* Use JWT access tokens for authenticated API requests.

* Store refresh tokens securely on the server.

* Support access-token renewal through refresh tokens.

* Support logout by invalidating the relevant refresh token.

* Restrict protected endpoints according to user roles and permissions.

* Prevent disabled accounts from accessing protected resources.

* Store passwords using an appropriate password-hashing algorithm rather than plaintext.

### 5.2 Patient Registration and Account Activation

Patient registration will be initiated by clinic staff.

The workflow shall be:

1. A receptionist creates a patient record.
2. The system generates a registration code associated with that patient.
3. The receptionist provides the code to the patient.
4. The patient uses the code to activate an account.
5. The system verifies the code and the required identity information.
6. The system links the new user account to the existing patient record.

Registration codes must:

* Be sufficiently unpredictable.

* Be associated with one patient.

* Expire after a defined period, initially proposed as 48–72 hours.

* Be usable only once.

* Be stored securely.

* Be invalidated after successful redemption.

* Be protected against repeated guessing attempts.

The system must not create a duplicate patient record when a patient activates an account.

### 5.3 Department Management

The clinic will have departments representing its medical specialties or service areas.

The system shall:

* Allow administrators to create and manage departments.

* Associate appointments with departments.

* Support department-based appointment booking.

* Allow authorized staff to manage a patient's eligible department when necessary.

A patient's initial department will be recorded during registration or the initial visit.

However, the system will not permanently restrict the patient to that department. Access to appointments in another department will depend on the clinic's authorization process.

### 5.4 Appointment Management

Patients will book appointments by selecting a date and an eligible department.

Patients will not select a specific doctor during the initial booking process.

The booking workflow shall be:

1. The patient selects a department and preferred date.
2. The system validates the booking request.
3. The system creates an appointment without a doctor assigned.
4. The receptionist reviews the appointment.
5. The receptionist assigns an appropriate doctor.
6. The patient can view the appointment and its assigned doctor.

The system shall:

* Associate every appointment with a patient.

* Associate every appointment with a department.

* Allow an appointment to have no assigned doctor initially.

* Allow authorized staff to assign or change the assigned doctor.

* Support appointment status tracking.

* Allow authorized appointment rescheduling and cancellation.

* Prevent unauthorized users from modifying appointments.

* Validate appointment dates and other booking constraints.

Appointment availability and capacity rules will be defined before implementing the booking logic.

The system must also define how cancellations, rescheduling, and appointment status changes are handled.

### 5.5 Medical Record Management

Doctors will be able to create medical reports for patients.

Each medical report shall be associated with:

* A patient.

* The doctor who authored it.

* The relevant appointment, where applicable.

* A creation timestamp.

* A report status.

Reports will support at least two states:

**Draft**

* The doctor may create and edit the report.

* The report is not yet finalized.

* Access is restricted to authorized users.

**Finalized**

* The report is treated as a completed clinical record.

* The doctor cannot directly edit the finalized report.

* The patient can view the report.

* The original report must be preserved.

If a finalized report requires correction, the system must support a traceable correction process rather than overwriting the original content.

The correction process should preserve the original report and record relevant information, including the correction, its author, and its timestamp.

Patients shall only be able to view finalized medical records belonging to their own patient records.

### 5.6 Patient Portal

The patient portal will provide access to the patient's own information.

Patients shall be able to:

* View their profile.

* View their appointments and appointment statuses.

* View assigned doctors when available.

* View finalized medical reports.

* View relevant medical history.

Patients shall not be able to:

* Create or edit clinical reports.

* Modify clinical observations.

* Access another patient's records.

* Assign doctors to appointments.

* Modify staff-managed information without authorization.

### 5.7 Nursing Functionality — Later Phase

Nursing functionality will be included in the project's future development plan.

Planned capabilities include recording:

* Blood pressure.

* Temperature.

* Pulse rate.

* Weight.

* Other relevant vital signs and nursing observations.

Nursing observations will be represented separately from doctors' medical reports.

The database design will account for this future functionality without requiring the full nursing workflow to be implemented in the first version.

## 6. Data Model Requirements

The database design will be finalized before implementing the SQLAlchemy models.

The following entities are expected to form the initial design.

### 6.1 User

Stores authentication and account information.

Expected responsibilities:

* Login credentials.

* User role.

* Account status.

* Account creation timestamp.

### 6.2 Patient

Stores patient-specific information independently of login credentials.

A patient record must be creatable before the patient has an account.

### 6.3 Doctor

Stores doctor-specific professional information and links it to the appropriate staff account.

### 6.4 Department

Represents the clinic's medical departments or specialties.

### 6.5 Appointment

Stores appointment information, including:

* Patient.

* Department.

* Assigned doctor, when available.

* Appointment date and time, as defined by the booking requirements.

* Appointment status.

* Creation and relevant update timestamps.

### 6.6 MedicalRecord

Stores doctors' clinical reports.

It must support draft and finalized states and preserve the relationship between a report, its author, and its patient.

### 6.7 PatientRegistrationCode

Stores information needed to issue and redeem patient account activation codes.

It must support expiration, single-use redemption, and secure verification.

### 6.8 RefreshToken

Stores the information necessary to manage server-side refresh-token validity and revocation.

### 6.9 AuditLog

The design should support recording important security-sensitive and clinical actions, including relevant account changes and medical-record finalization or correction events.

The exact fields and scope of audit logging will be defined during database design.

### 6.10 Future Nursing Entity

A separate entity, such as `VitalSign` or `NursingObservation`, may be introduced to store nursing observations.

Its fields and relationships will be finalized when the nursing feature is implemented.

## 7. Non-Functional Requirements

### 7.1 Security

The system shall:

* Enforce authentication and authorization.

* Validate incoming request data.

* Protect passwords and authentication tokens.

* Prevent patients from accessing other patients' records.

* Restrict clinical information to authorized users.

* Protect registration-code redemption against guessing and replay.

* Avoid exposing sensitive information through error messages or logs.

### 7.2 Privacy

The project will be developed using fictional patient information.

The system's privacy and data-handling design will take Nigeria's applicable data-protection requirements, including the Nigeria Data Protection Act 2023, into consideration.

### 7.3 Data Integrity

The system shall:

* Enforce appropriate database constraints.

* Prevent invalid relationships between records.

* Validate appointment and medical-record operations.

* Preserve finalized medical reports.

* Prevent duplicate account activation using the same registration code.

### 7.4 Maintainability

The codebase shall:

* Use a clear and consistent project structure.

* Separate API routing, business logic, database access, and data validation where appropriate.

* Use SQLAlchemy models for database entities.

* Use Alembic for database schema migrations.

* Include meaningful error handling.

* Include automated tests for important business rules and security boundaries.

### 7.5 API Documentation

The API shall provide interactive documentation through FastAPI's OpenAPI integration.

Endpoints, request schemas, response schemas, authentication requirements, and relevant error responses should be documented.

## 8. Scope of the First Version

The first version will prioritize:

1. Authentication and role-based authorization.
2. Staff account management.
3. Patient registration and account activation.
4. Department management.
5. Patient appointment booking.
6. Receptionist assignment of doctors.
7. Appointment status management.
8. Doctor medical-report creation and finalization.
9. Patient access to finalized medical records.
10. Basic security, validation, testing, and auditability.

## 9. Features Planned for Later

The following features are outside the initial implementation scope:

* Nurse-specific workflows and vital-sign recording.

* Advanced appointment availability and scheduling.

* Automated appointment reminders.

* Email and SMS notifications.

* Advanced reporting and analytics.

* Additional clinical workflows.

* More advanced audit-log review tools.

These features may be added after the core system is implemented and tested.

## 10. Development Approach

Development will proceed in the following order:

1. Finalize requirements and resolve remaining business rules.
2. Design the database entities, fields, relationships, and constraints.
3. Implement the SQLAlchemy models.
4. Configure Alembic and create the initial database migration.
5. Implement authentication and authorization.
6. Implement patient registration and account activation.
7. Implement department and appointment management.
8. Implement medical-record creation, finalization, and patient access.
9. Write and run automated tests.
10. Review security, documentation, and project quality.
11. Introduce planned features in subsequent iterations.

