console.log 'header.coffee'

# TODO: widget-ify this kind of overflow nav

$window = $(window)
$nav    = $('#site-header .category_nav')

FIXED_ORDER = ['startups', 'accelerators', 'video']
first_categories = {}
other_categories = []

_.each params.categories, (cat) ->
    if cat.slug in FIXED_ORDER
        first_categories[cat.slug] = (cat)
    else
        other_categories.push(cat)
first_categories = _.map FIXED_ORDER, (slug) -> first_categories[slug]


$popover = $("""
        <div class="popover">
            <span class="popover_trigger">More</span>
            <div class="popover_content"></div>
        </div>
    """)

$popover_content = $popover.find('.popover_content')
$popover_trigger = $popover.find('.popover_trigger')

$popover_trigger.on 'touchend', ->
    _.defer ->
        if $popover.attr('data-active')
            $popover.removeAttr('data-active')
        else
            $popover.attr('data-active', true)

makeCategoryLink = (cat) ->
    return "<a href='/category/#{ cat.slug }/'>#{ cat.title }</a>"



renderPopover = (lists...) ->
    $popover_content.empty()
    for list in lists
        _.each list, (cat) ->
            $popover_content.append(makeCategoryLink(cat))



renderNav = ->
    $nav.empty()
    if $window.width() <= 700
        console.log 'all in'
        renderPopover(first_categories, other_categories)
        $popover_trigger.text('Categories')
    else
        _.each first_categories, (cat) ->
            $nav.append(makeCategoryLink(cat))
        renderPopover(other_categories)
        $popover_trigger.text('More')
    $nav.append($popover)



$window.on 'resize', _.debounce(renderNav, 50)
renderNav()


