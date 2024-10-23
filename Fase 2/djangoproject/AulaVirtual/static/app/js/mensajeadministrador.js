function confirmDelete(unidadId, unidadNombre) {
    Swal.fire({
        title: '¿Estás seguro?',
        text: "Estás a punto de eliminar la unidad: " + unidadNombre,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            // Redirigir a la vista de eliminación si se confirma
            window.location.href = '/adminunidadeliminar/' + unidadId + '/';
        }
    });
}
