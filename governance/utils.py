
from django.utils.timezone import now
from django.db.models import Q
from governance.models import GovernanceMember, GovernanceMemberRole

ROLE_HIERARCHY = {
    "PRESIDENT": ["TREASURER", "SECRETARY", "MEMBER", "OTHER"],
    "TREASURER": ["ASSISTANT_TREASURER"],
    "SECRETARY": ["ASSISTANT_SECRETARY"],
    "ASSISTANT_TREASURER": [],
    "ASSISTANT_SECRETARY": [],
    "MEMBER": [],
    "OTHER": [],
}

ROLE_COLORS = {
    "PRESIDENT": "#90caf9",
    "TREASURER": "#2e7d32",
    "SECRETARY": "#2e7d32",
    "ASSISTANT_TREASURER": "#66bb6a",
    "ASSISTANT_SECRETARY": "#66bb6a",
    "MEMBER": "#e0e0e0",
    "OTHER": "#f3e5f5",
}

def create_node(member_data):
    return {
        "employee": {
            "id": member_data["id"],
            "firstName": member_data["first_name"],
            "lastName": member_data["last_name"],
            "email": member_data["email"],
            "role_code": member_data["role_code"],
            "role": member_data["role_label"],
            "photo": member_data["photo"],
        },
        "color": ROLE_COLORS.get(member_data["role_code"], "#e0e0e0"),
        "children": [],
    }

def build_governance_organization_tree(info):
    user = info.context.user
    company = user.the_current_company
    today = now()
    members = GovernanceMember.objects.filter(
        is_active=True,
        is_archived=False,
        is_deleted=False,
        company=company
    ).filter(
        Q(
            governance_member_roles__starting_date_time__lte=today,
            governance_member_roles__ending_date_time__gte=today
        )
        | Q(
            governance_member_roles__starting_date_time__lte=today,
            governance_member_roles__ending_date_time__isnull=True
        )
        | Q(governance_member_roles__isnull=True)  # <- inclure ceux sans aucun rôle
    ).distinct()
    role_label_map = dict(GovernanceMemberRole.ROLE_CHOICES)

    member_data = []
    for member in members:
        current = member.governance_member_roles.filter(
            starting_date_time__lte=now()
        ).filter(
            Q(ending_date_time__gte=now()) | Q(ending_date_time__isnull=True)
        ).order_by('-starting_date_time').first()

        if current:
            role_code = current.role
            label = role_label_map.get(role_code, 'Membre')
            if role_code == "OTHER":
                label = current.other_role
        else:
            role_code = "MEMBER"
            label = "Membre"

        member_data.append({
            "id": member.id,
            "first_name": member.first_name,
            "last_name": member.last_name,
            "email": member.email,
            "role_code": role_code,
            "role_label": label,
            "photo": info.context.build_absolute_uri(member.photo.image.url) if member.photo else None ,
        })

    grouped_by_role = {}
    for m in member_data:
        grouped_by_role.setdefault(m["role_code"], []).append(m)

    presidents = grouped_by_role.get("PRESIDENT", [])
    if not presidents:
        return None

    president = presidents[0]
    tree = create_node(president)

    def add_children(parent_role, parent_node):
        child_roles = ROLE_HIERARCHY.get(parent_role, [])
        for role in child_roles:
            for child_member in grouped_by_role.get(role, []):
                child_node = create_node(child_member)
                parent_node["children"].append(child_node)
                add_children(role, child_node)

    add_children("PRESIDENT", tree)
    return tree
