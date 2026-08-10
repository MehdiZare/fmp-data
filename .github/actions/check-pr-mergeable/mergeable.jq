# Shared REST → TSV extraction for check-pr-mergeable (#216 / #223).
# Input: GitHub pull object (or mock JSON with mergeable + mergeable_state).
# Output: single TSV line: mergeable\tmergeable_state
#
# - JSON null mergeable → literal token "null" (not empty @tsv field)
# - null mergeable_state → "unknown" (unresolved retry path; fail closed)
[(.mergeable | tostring), ((.mergeable_state // "unknown") | tostring)] | @tsv
