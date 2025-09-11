import { TenantTable } from "./tenant-table";
import { columns } from "./columns";

export default function TenantsPage() {
  return (
    <div className="container mx-auto py-10">
      <h1 className="text-2xl font-bold mb-4">Gestión de Inquilinos</h1>
      <TenantTable columns={columns} />
    </div>
  );
}