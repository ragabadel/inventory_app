from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory.models import UserProfile
from django.db import transaction

class Command(BaseCommand):
    help = 'Creates UserProfile instances for users that do not have one'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Create profile for specific username',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreate profiles even if they exist',
        )

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                if options['username']:
                    try:
                        user = User.objects.get(username=options['username'])
                        self._create_profile_for_user(user, force=options['force'])
                    except User.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f'User {options["username"]} does not exist'))
                        return
                else:
                    users = User.objects.all()
                    profiles_created = 0
                    for user in users:
                        if self._create_profile_for_user(user, force=options['force']):
                            profiles_created += 1
                    
                    self.stdout.write(self.style.SUCCESS(f'Successfully created {profiles_created} user profiles'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating user profiles: {str(e)}'))

    def _create_profile_for_user(self, user, force=False):
        try:
            if force:
                UserProfile.objects.filter(user=user).delete()
                UserProfile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f'Recreated profile for user: {user.username}'))
                return True
            else:
                try:
                    user.profile
                    self.stdout.write(f'Profile already exists for user: {user.username}')
                    return False
                except UserProfile.DoesNotExist:
                    UserProfile.objects.create(user=user)
                    self.stdout.write(self.style.SUCCESS(f'Created profile for user: {user.username}'))
                    return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating profile for user {user.username}: {str(e)}'))
            return False 