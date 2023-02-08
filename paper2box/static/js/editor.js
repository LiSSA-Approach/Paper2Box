// Content element in which the editor will reside in
const content = document.querySelector('#content');
// Get diagram element where all the objects will reside in
const diagram = document.querySelector('#diagram');

// Svg namespace
const svgn = "http://www.w3.org/2000/svg";
// Get svg element
const svg = document.querySelector('#svg-space');

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
        // Update dragged element to accomodate for dynamic changes such as connections etc.
        if(dragged != diagram) getObjectFromId(dragged.id).update();

        // Update last mouse position for next drag event
        last_mousepos = [event.clientX, event.clientY];
    }
}

function offclick(event) {
    // Unregister dragged element
    dragged = null;
}

function get_selected()
{
    // Return diagram if no selected object or selected object is of type connection
    let _selected = selected?getObjectFromId(selected.id):diagram;
    return _selected._class=='Connection'?diagram:_selected
}
function create_classnode(event) {
    let _obj = new ClassNode(0, 0, 300, 200, get_selected());
    _obj.setPos(0, 0);
    select(_obj.bbox);
}
function create_label(event) {
    let _obj = new Label(0, 0, 250, 75, "Label", get_selected());
    _obj.setPos(0, 0);
    select(_obj.bbox);
}
function create_package(event) {
    let _obj = new PackageNode(0, 0, 500, 150, get_selected());
    _obj.setPos(0, 0);
    select(_obj.bbox);
}
function create_connection(event) {
    let _obj = new Connection(0, 0, 500, 150, diagram);
    _obj.setPos(0, 0);
    select(_obj.bbox);
}
function delete_selection(event) {
    if(selected && objectDict[selected.id])
        objectDict[selected.id].delete();
}
let json_area_on = false;
function json_out(event) {
    json_area_on = !json_area_on;
    document.querySelector('#json-area').style.display = json_area_on?"flex":"none";
}
function register(object) {
    objectDict[object.bbox.id] = object;
}
function unregister(object)
{
    objectDict[object.bbox.id] = null;
}
function getObjectFromId(id)
{
    if(objectDict[id]) return objectDict[selected.id];
    else return diagram;
}


// Setting up events
diagram.onmousedown = onclick;
diagram.onmousemove = onmove;
diagram.onmouseup = offclick;
document.querySelector('#classnode-button').onclick = create_classnode;
document.querySelector('#label-button').onclick = create_label;
document.querySelector('#package-button').onclick = create_package;
document.querySelector('#connection-button').onclick = create_connection;
document.querySelector('#delete-button').onclick = delete_selection;
document.querySelector('#json-button').onclick = json_out;
document.querySelector('#json-ctc').onclick = function(event) {
    navigator.clipboard.writeText(json_conversion());
}
document.querySelector('#json-form').disabled = true;

/*
JSON conversion
*/
function json_conversion()
{
    let out = [];
    // Get all root nodes
    for(let i = 0; i <rootNodes.length; i++) {
        node_json = rootNodes[i].to_json();
        if(node_json) out.push(node_json);
    }
    // Return prettified JSON
    return JSON.stringify(out, null, '\t');
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
        for(child of this.children) if(child.active) child.delete();
        this.bbox.remove();
        unregister(this);
        this.active = false;
        if(rootNodes.includes(this)) rootNodes.splice(rootNodes.indexOf(this), 1);
    }

    update_style() {
        this.bbox.style.cssText = 'left: ' + this.topleft[0]/2 + 'px; top: ' + this.topleft[1]/2 + 'px; width: '
                + this.size[0]/2 + 'px; height: ' + this.size[1]/2 + 'px;';
    }
    // Override this:
    update() {}
    getPos()
    {
        let x = parseFloat(this.bbox.style.left)*2;
        let y = parseFloat(this.bbox.style.top)*2;
        if(this.parent.id != "diagram") {
            x += this.parent.getPos()[0];
            y += this.parent.getPos()[1];
        }
        return [x, y];
    }
    getSize()
    {
        return [parseFloat(this.bbox.style.width)*2, parseFloat(this.bbox.style.height)*2]
    }
    to_json(ignore_children = false)
    {
        // Get children
        let children = [];
        if(!ignore_children)
        for(let i = 0; i < this.children.length; i++)
            if(this.children[i].active) children.push(this.children[i].to_json());

        let out = {};
        // Get class of object
        out['class'] = this._class;
        if(this._class == 'Label') out['text'] = this.labeltext.value;
        // Get position and size
        out['XYXY'] = [this.getPos()[0],
                       this.getPos()[1],
                       this.getPos()[0]+this.getSize()[0],
                       this.getPos()[1]+this.getSize()[1]];

        out['children'] = children;
        return out;
    }

    constructor(x1, y1, x2, y2, parent=diagram, _class="ClassNode")
    {
        if(parent.bbox) this.topleft = [x1-parent.topleft[0], y1-parent.topleft[1]];
        else this.topleft = [x1, y1];
        this.size = [x2 - x1, y2 - y1];
        this.children = [];
        this.parent = parent;
        this.id = id++;
        this._class = _class;
        this.active = true;

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
    constructor(x1, y1, x2, y2, text="Label", parent=diagram, _class="Label") {
        super(x1, y1, x2, y2, parent, _class);
        this.bbox.classList.add('Label');

        // Create label text
        this.text = text;
        this.labeltext = document.createElement('textarea');
        this.labeltext.value = text;
        this.labeltext.classList.add('Label-text');
        this.bbox.appendChild(this.labeltext);
    }
}

class ClassNode extends Node {
    constructor(x1, y1, x2, y2, parent=diagram, _class="ClassNode") {
        super(x1, y1, x2, y2, parent);
    }
}

class PackageNode extends Node {
    constructor(x1, y1, x2, y2, parent=diagram, _class="PackageNode") {
        super(x1, y1, x2, y2, parent, _class);
        this.bbox.classList.add('PackageNode');
    }
}

// Might be added later
class AggregationNode extends Node {}
class CompsitionNode extends Node {}
class RealizationNode extends Node {}

class Connection extends Node {
    constructor(x1, y1, x2, y2, direction='up', parent=diagram, _class="Connection") {
        super(x1, y1, x1+50, y1+50, parent, _class);

        // Create seccond node that connection will be pointing to
        this.seccond_node = new Node(x2, y2, x2+50, y2+50, diagram, _class);
        // Manually unregister seccond node from rootnodes
        rootNodes.splice(rootNodes.indexOf(this.seccond_node), 1);

        // Adding update event to seccond_node so that when it will be dragged it will also update the line
        this.seccond_node.update = () => { this.seccond_node.children[0].update(); };

        // Manually adding childreen to avoid them being hieracycally ordered in html
        this.seccond_node.children.push(this);

        // Create circle to drag connection with
        this.bbox.classList.add('Connection');
        this.seccond_node.bbox.classList.add('Connection');

        // Create line
        this.line = document.createElementNS(svgn, 'line');
        this.line.setAttribute('stroke-width', '5px');
        this.line.setAttribute('stroke', '#00000080');
        svg.appendChild(this.line);

        // Update the line
        this.update();
    }

    update()
    {
        this.line.setAttribute('x1', this.getPos()[0]/2+12.5);
        this.line.setAttribute('y1', this.getPos()[1]/2+12.5);

        this.line.setAttribute('x2', this.seccond_node.getPos()[0]/2+12.5);
        this.line.setAttribute('y2', this.seccond_node.getPos()[1]/2+12.5);
    }

    delete()
    {
        // Delete line
        this.line.remove();
        // Delete self
        super.delete()
        // Delete second part of connection
        this.seccond_node.delete();
    }

    getSize()
    {
        let x = this.seccond_node.getPos()[0]-this.getPos()[0];
        let y = this.seccond_node.getPos()[1]-this.getPos()[1];
        return [x, y];
    }

    to_json(ignore_children = false) {
        return super.to_json(true);
    }
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
                let _classnode = new ClassNode(0, 0, child.XYXY[2]-child.XYXY[0], child.XYXY[3]-child.XYXY[1], parent);
                _classnode.setPos(child.XYXY[0]-object.XYXY[0], child.XYXY[1]-object.XYXY[1]);
                initChildreen(child, _classnode);
                break;
            case "Label":
                let _label = new Label(0, 0, child.XYXY[2]-child.XYXY[0], child.XYXY[3]-child.XYXY[1], child.text, parent);
                _label.setPos(child.XYXY[0]-object.XYXY[0], child.XYXY[1]-object.XYXY[1]);
                initChildreen(child, _label);
                break;
            case "PackageNode":
                let _packagenode = new PackageNode(0, 0, child.XYXY[2]-child.XYXY[0], child.XYXY[3]-child.XYXY[1], child.text, parent);
                _packagenode.setPos(child.XYXY[0]-object.XYXY[0], child.XYXY[1]-object.XYXY[1]);
                initChildreen(child, _packagenode);
                break;
            case "Connection":
                let _connection = new Connection(object.XYXY[0], object.XYXY[1], object.XYXY[2], object.XYXY[3], object.direction, parent);
                _connection.setPos(child.XYXY[0]-object.XYXY[0], child.XYXY[1]-object.XYXY[1]);
                initChildreen(object, _connection)
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
        case "PackageNode":
            let _packagenode = new PackageNode(object.XYXY[0], object.XYXY[1], object.XYXY[2], object.XYXY[3], object.text);
            initChildreen(object, _packagenode)
            break;
        case "NAryAssociationDiamond":
        case "Aggregation":
        case "Composition":
        case "Extension":
        case "Dependency":
        case "Realization":
        case "CommentConnection":
        case "AssociationUnidirectional":
        case "AssociationBidirectional":
        case "Connection":
            let _connection = new Connection(object.XYXY[0], object.XYXY[1], object.XYXY[2], object.XYXY[3], object.direction);
            initChildreen(object, _connection)
            break;
    }
}