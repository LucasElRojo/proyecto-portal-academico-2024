
function eliminarUsuario(id){
    Swal.fire({
        title: '¿Estas seguro de eliminar el Usuario?',
        text: "Esto no se puede revertir!",
        icon: 'warning',  
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Si, eliminalo!'
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire(
                'Eliminado!',
                'El Usuario ha sido eliminado.',
                'success'
            ).then(function() {
                window.location.href = "/eliminarUsuario/"+id+"/"
            });
        }
    });
}