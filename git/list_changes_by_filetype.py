import pydriller

changes = {}

for commit in pydriller.RepositoryMining('.').traverse_commits():
    for modification in commit.modifications:
        date = commit.committer_date.strftime('%Y-%m-%d')
        if '.rb' in modification.filename or '.feature' in modification.filename:
            if date not in changes:
                changes[date] = {
                    'rb': 0,
                    'feature': 0,
                }

            if '.rb' in modification.filename:
                changes[date]['rb'] += modification.added
                changes[date]['rb'] -= modification.removed

            if '.feature' in modification.filename:
                changes[date]['feature'] += modification.added
                changes[date]['feature'] -= modification.removed

print('date,ruby,feature')
for date in changes:
    print('{},{},{}'.format(date,
                            changes[date]['rb'], changes[date]['feature']))
