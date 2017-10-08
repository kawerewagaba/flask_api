"""empty message

Revision ID: 6609bd0935c7
Revises: 19907545b510
Create Date: 2017-10-08 00:58:04.762985

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6609bd0935c7'
down_revision = '19907545b510'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=256), nullable=False),
    sa.Column('bucketlist', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['bucketlist'], ['bucketlists.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('description')
    )
    op.add_column('bucketlists', sa.Column('user', sa.Integer(), nullable=False))
    op.alter_column('bucketlists', 'name',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.create_unique_constraint(None, 'bucketlists', ['name'])
    op.create_foreign_key(None, 'bucketlists', 'users', ['user'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'bucketlists', type_='foreignkey')
    op.drop_constraint(None, 'bucketlists', type_='unique')
    op.alter_column('bucketlists', 'name',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.drop_column('bucketlists', 'user')
    op.drop_table('items')
    # ### end Alembic commands ###