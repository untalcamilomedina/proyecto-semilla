import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { User } from '@/types/api';

interface RecentUsersProps {
  users: User[];
}

export function RecentUsers({ users }: RecentUsersProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Usuarios Recientes</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-8">
        {users.map((user) => (
          <div key={user.id} className="flex items-center gap-4">
            <Avatar className="hidden h-9 w-9 sm:flex">
              <AvatarImage src={user.avatar} alt="Avatar" />
              <AvatarFallback>{user.full_name ? user.full_name[0] : 'U'}</AvatarFallback>
            </Avatar>
            <div className="grid gap-1">
              <p className="text-sm font-medium leading-none">{user.full_name || 'Usuario'}</p>
              <p className="text-sm text-muted-foreground">{user.email}</p>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}