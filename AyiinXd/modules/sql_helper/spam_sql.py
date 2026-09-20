from AyiinXd.modules.sql_helper import BASE, SESSION

from sqlalchemy import Column, String, Integer, Boolean, inspect, text


class SpamList(BASE):
    __tablename__ = "spam_list"

    name = Column(String, primary_key=True)
    type = Column(String, default="spam")
    content = Column(String, default="")
    delay = Column(Integer, default=60)
    is_active = Column(Boolean, default=False)


class SpamGroup(BASE):
    __tablename__ = "spam_group"

    id = Column(Integer, primary_key=True, autoincrement=True)
    list_name = Column(String, nullable=False)
    group_username = Column(String, nullable=False)


def commit_db():
    try:
        SESSION.commit()
    except Exception:
        SESSION.rollback()
        raise


def add_list(name, jenis="spam", content="", delay=60):
    data = SESSION.query(SpamList).filter_by(name=name).first()

    if data:
        data.type = jenis
        data.content = content
        data.delay = delay
    else:
        SESSION.add(
            SpamList(
                name=name,
                type=jenis,
                content=content,
                delay=delay,
                is_active=False
            )
        )

    commit_db()


def get_list(name):
    return SESSION.query(SpamList).filter_by(name=name).first()


def get_all_lists():
    return SESSION.query(SpamList).all()


def update_list(name, jenis, delay, content):
    data = get_list(name)

    if not data:
        return False

    data.type = jenis
    data.delay = delay
    data.content = content

    commit_db()
    return True


def set_active(name, status=True):
    data = get_list(name)

    if data:
        data.is_active = status
        commit_db()


def delete_list(name):
    SESSION.query(SpamGroup).filter_by(list_name=name).delete()
    SESSION.query(SpamList).filter_by(name=name).delete()
    commit_db()


def add_groups_to_list(name, groups):
    for group in groups:
        exists = SESSION.query(SpamGroup).filter_by(
            list_name=name,
            group_username=group
        ).first()

        if not exists:
            SESSION.add(
                SpamGroup(
                    list_name=name,
                    group_username=group
                )
            )

    commit_db()


def get_groups(name):
    return [
        x.group_username
        for x in SESSION.query(SpamGroup)
        .filter_by(list_name=name)
        .all()
    ]


def delete_group(name, group):
    SESSION.query(SpamGroup).filter_by(
        list_name=name,
        group_username=group
    ).delete()

    commit_db()


def migrate():
    engine = SESSION.get_bind()
    inspector = inspect(engine)

    if "spam_list" not in inspector.get_table_names():
        BASE.metadata.create_all(bind=engine)
        return

    columns = [
        x["name"]
        for x in inspector.get_columns("spam_list")
    ]

    with engine.begin() as conn:

        if "type" not in columns:
            conn.execute(
                text(
                    "ALTER TABLE spam_list ADD COLUMN type VARCHAR"
                )
            )

        if "content" not in columns:
            conn.execute(
                text(
                    "ALTER TABLE spam_list ADD COLUMN content TEXT"
                )
            )

        if "delay" not in columns:
            conn.execute(
                text(
                    "ALTER TABLE spam_list ADD COLUMN delay INTEGER DEFAULT 60"
                )
            )

        if "is_active" not in columns:
            conn.execute(
                text(
                    "ALTER TABLE spam_list ADD COLUMN is_active BOOLEAN DEFAULT FALSE"
                )
            )


BASE.metadata.create_all(bind=SESSION.get_bind())
migrate()
