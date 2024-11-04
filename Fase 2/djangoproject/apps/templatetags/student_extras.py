from django import template

register = template.Library()

@register.filter
def unique_subjects(attendances):
    """Return a unique list of subjects from attendance records."""
    seen_subjects = set()
    unique_list = []
    for attendance in attendances:
        subject_name = attendance.subject.name
        if subject_name not in seen_subjects:
            unique_list.append(subject_name)
            seen_subjects.add(subject_name)
    return unique_list

@register.filter
def unique_students(attendances):
    """Return a unique list of students (full names) from attendance records."""
    seen_students = set()
    unique_list = []
    for attendance in attendances:
        full_name = f"{attendance.student.nombres} {attendance.student.apellido_paterno} {attendance.student.apellido_materno}"
        if full_name not in seen_students:
            unique_list.append(full_name)
            seen_students.add(full_name)
    return unique_list
