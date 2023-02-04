// Get diagram object where all the objects will reside in
const diagram = document.querySelector('#diagram');
// Get objects from json
let objects = JSON.parse(diagram.innerHTML);
diagram.innerHTML = "";
// ids for objects
let id = 0

// Get basic diagram specs
const diagram_width = diagram.clientWidth;
const diagram_height = diagram.clientHeight;

// Bbox : Node
let objectDict = {};
// All nodes with no parent object: Important for json formatting after editing
let rootNodes = [];



/*
Events
*/

// Element being currently dragged
let dragged = null;
// Element having been last clicked on
let selected = null;
let last_mousepos = [0, 0];
function select(target) {
    // Unregister last selected object
    if(selected) selected.classList.remove('Node-selected');

    // Register new selected object
    selected = target;
    selected.classList.add('Node-selected');
}
function onclick(event) {
    // Register new element being dragged
    dragged = event.target;
    last_mousepos = [event.clientX, event.clientY];

    select(event.target);
}
function onmove(event) {
    if(dragged)
    {
        // Move element to where it's being dragged to
        dragged.style.left = (parseFloat(dragged.style.left) + event.clientX-last_mousepos[0]) + "px";
        dragged.style.top = (parseFloat(dragged.style.top) + event.clientY-last_mousepos[1]) + "px";
        // Keep it in bounds of parent element
        if(dragged.parentElement != diagram) {
            dragged.style.left = Math.min(Math.max(-2, parseFloat(dragged.style.left)),
                                          parseFloat(dragged.parentElement.style.width)-
                                          parseFloat(dragged.style.width)-2) + "px";
            dragged.style.top = Math.min(Math.max(-2, parseFloat(dragged.style.top)),
                                          parseFloat(dragged.parentElement.style.height)-
                                          parseFloat(dragged.style.height)-2) + "px";
        }
        // Update last mouse position for next drag event
        last_mousepos = [event.clientX, event.clientY];
    }
}

function offclick(event) {
    // Unregister dragged element
    dragged = null;
}

function create_classnode(event) {
    console.log(selected.id, selected.style.left, selected.style.top);
    let _obj = new ClassNode(0, 0, 300, 200, selected?objectDict[selected.id]:diagram);
    _obj.setPos(0, 0);
    select(_obj.bbox);
}
function create_label(event) {
    let _obj = new Label(0, 0, 250, 75, "Label", selected?objectDict[selected.id]:diagram);
    _obj.setPos(0, 0);
    select(_obj.bbox);
}
function delete_selection(event) {
    if(selected && objectDict[selected.id])
        objectDict[selected.id].delete();

}
function register(object) {
    objectDict[object.bbox.id] = object;
}
function unregister(object)
{
    objectDict[object.bbox.id] = null;
}

// Setting up events
diagram.onmousedown = onclick;
diagram.onmousemove = onmove;
diagram.onmouseup = offclick;
document.querySelector('#classnode-button').onclick = create_classnode;
document.querySelector('#label-button').onclick = create_label;
document.querySelector('#delete-button').onclick = delete_selection;



/*
JSON conversion
*/
function json_conversion()
{
    let out = [];
}
function convert_object(object)
{
    // Get children
    children = [];
    for(child of object.children)
        children.push(convert_object(children));

    out = {};
    out['class'] = object.class;
    out['children'] = children;
}


/*
Classes
*/

// Class declarations

class Node {
    setPos(x, y)
    {
        this.topleft = [x, y];
        this.update_style();
    }
    set_size(width, height) {
        this.size = [width, height];
        this.update_style();
    }

    delete() {
        for(child of this.children) child.delete();
        this.bbox.remove();
        unregister(this);
        if(rootNodes.includes(this)) rootNodes.splice(rootNodes.indexOf(this), 1);
    }

    update_style() {
        this.bbox.style.cssText = 'left: ' + this.topleft[0]/2 + 'px; top: ' + this.topleft[1]/2 + 'px; width: '
        + this.size[0]/2 + 'px; height: ' + this.size[1]/2 + 'px;';
    }

    constructor(x1, y1, x2, y2, parent=diagram, _class="classNode")
    {
        if(parent.bbox) this.topleft = [x1-parent.topleft[0], y1-parent.topleft[1]];
        else this.topleft = [x1, y1];
        this.size = [x2 - x1, y2 - y1];
        this.children = [];
        this.parent = parent;
        this.id = id++;

        // Create basic bbox aka resizable border + background
        this.bbox = document.createElement('div');
        this.bbox.classList.add('Node');
        this.bbox.setAttribute("id", "node-"+id);
        this.update_style();

        // Spawn object either as child of diagram or child of selected parent
        if(parent.id != 'diagram') {
            parent.bbox.appendChild(this.bbox);
            parent.children.push(this);
        }
        else {
            parent.appendChild(this.bbox);
            rootNodes.push(this);
        }

        this.bbox.onmousedown = onclick;
        this.bbox.ondragstart = function(event) { event.preventDefault(); };

        // Register bbox with Node
        register(this);
    }
}

class Label extends Node {
    constructor(x1, y1, x2, y2, text="Label", parent=diagram) {
        super(x1, y1, x2, y2, parent);
        this.bbox.classList.add('Label');

        // Create label text
        this.text= text;
        this.labeltext = document.createElement('textarea');
        this.labeltext.value = text;
        this.labeltext.classList.add('Label-text');
        this.bbox.appendChild(this.labeltext);
    }
}

class ClassNode extends Node {
    constructor(x1, y1, x2, y2, parent=diagram) {
        super(x1, y1, x2, y2, parent);
    }
}

class PackageNode extends Node {

}

class AggregationNode extends Node {

}

class CompsitionNode extends Node {

}

class RealizationNode extends Node {

}

class AssociationNode extends Node {

}




/*
Object instantiation
*/

// Instantiating elements from json

function initChildreen(object, parent)
{
    for(child of object.children)
        switch(child.class) {
            case "ClassNode":
                let _classnode = new ClassNode(child.XYXY[0]-object.XYXY[0], child.XYXY[1]-object.XYXY[1], child.XYXY[2], child.XYXY[3], parent);
                    initChildreen(child, _classnode);
                    parent.children.push(_classnode);
                    break;
                case "Label":
                    let _label = new Label(child.XYXY[0]-object.XYXY[0], child.XYXY[1]-object.XYXY[1], child.XYXY[2], child.XYXY[3], child.text, parent);
                    initChildreen(child, _label);
                    parent.children.push(_label);
                    break;
    }
}


// Initialize root objects with no parents
for(object of objects)
{
    switch(object.class) {
        case "ClassNode":
            let _classnode = new ClassNode(object.XYXY[0], object.XYXY[1], object.XYXY[2],object.XYXY[3]);
            initChildreen(object, _classnode)
            break;
        case "Label":
            let _label = new Label(object.XYXY[0], object.XYXY[1], object.XYXY[2], object.XYXY[3], object.text);
            initChildreen(object, _label)
            break;
    }
}