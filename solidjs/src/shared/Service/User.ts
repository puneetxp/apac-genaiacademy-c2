import { ModelService } from "./ModelService";
import { User } from "../Interface/Model/User";
import { Role } from "../Interface/Model/Role";
import { Active_role } from "../Interface/Model/Active_role";

export const UserService = (new ModelService<User>())
    .seTable("user")
    .seturl("api/user");

export const RoleService = (new ModelService<Role>())
    .seTable("role")
    .seturl("api/role");

export const Active_roleService = (new ModelService<Active_role>())
    .seTable("active_role")
    .seturl("api/active_role");
