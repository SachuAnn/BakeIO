def role_redirect(user):
    if user.role == 'customer':
        return '/auth/dashboard/customer/'
    elif user.role == 'bakery':
        return '/bakery/dashboard/'
    elif user.role == 'delivery':
        return '/delivery/dashboard/'
    elif user.role == 'admin':
        return '/auth/dashboard/admin/'
    return '/'
