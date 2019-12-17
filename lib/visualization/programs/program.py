import OpenGL.GL as gl
from abc import ABC, abstractmethod
import numpy as np

from lib.swarm_sim_header import eeprint, eprint
from lib.visualization.utils import load_obj_file


class Program(ABC):

    def __init__(self, vertex_file, fragment_file, model_file):
        """
        Superclass for Opengl Programs.
        compiles the given shader source files, gives access to the shared uniform variables of the shaders,
        loads the model mesh and calls the abstract init_buffer function with the loaded data
        :param vertex_file: file path to the vertex shader
        :param fragment_file: file path to the fragment shader
        :param model_file: file path to the .obj file
        """
        # creating GL Program
        self._program = gl.glCreateProgram()
        # loading shader source files
        self._vertex = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        self._fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        try:
            vert_source = open(vertex_file).read()
            frag_source = open(fragment_file).read()
            self._init_shaders(vert_source, frag_source)
        except IOError as e:
            eeprint("ERROR: vertex or fragment shader file couldn't be loaded:\n%s" % str(e))
        gl.glUseProgram(self._program)

        self.light_angle = 0
        v, n, t = load_obj_file("lib/visualization/models/"+model_file)
        self.size = len(v)

        self._vao = gl.glGenVertexArrays(1)
        self.use()
        self._init_buffers(v, n, t)
        gl.glBindVertexArray(0)

        self._init_uniforms()

    def _init_uniforms(self):
        """
        initializes the shader uniform variables
        :return:
        """
        eye = np.eye(4, 4)
        self.set_projection_matrix(eye)
        self.set_view_matrix(eye)
        self.set_world_matrix(eye)
        self.set_world_scaling((1.0, 1.0, 1.0))
        self.rotate_light(0.0)
        self.set_model_scaling((1.0, 1.0, 1.0))
        self.set_ambient_light(0.2)
        self.set_light_color((1.0, 1.0, 1.0, 1.0))

    @abstractmethod
    def _init_buffers(self, verts, norms, uvs):
        """
        creates the vbos and uploads the model data
        :param verts: the model positional vectors
        :param norms: the model face normals
        :param uvs: the model texture coordinates
        :return:
        """
        pass

    def _init_shaders(self, vert, frag):
        """
        compiles and links shaders
        :param vert: vertex shader source string
        :param frag: fragment shader source string
        :return:
        """
        # set the sources
        gl.glShaderSource(self._vertex, vert)
        gl.glShaderSource(self._fragment, frag)
        # compile vertex shader
        gl.glCompileShader(self._vertex)
        if not gl.glGetShaderiv(self._vertex, gl.GL_COMPILE_STATUS):
            e = gl.glGetShaderInfoLog(self._vertex).decode()
            eeprint("COMPILATION ERROR: vertex shader couldn't be compiled:\n%s" % str(e))

        # compile fragment shader
        gl.glCompileShader(self._fragment)
        if not gl.glGetShaderiv(self._fragment, gl.GL_COMPILE_STATUS):
            e = gl.glGetShaderInfoLog(self._fragment).decode()
            eeprint("COMPILATION ERROR: fragment shader couldn't be compiled:\n%s" % str(e))

        # attach the shaders to the matter program
        gl.glAttachShader(self._program, self._vertex)
        gl.glAttachShader(self._program, self._fragment)

        # link the shaders to the matter program
        gl.glLinkProgram(self._program)
        if not gl.glGetProgramiv(self._program, gl.GL_LINK_STATUS):
            e = gl.glGetProgramInfoLog(self._program)
            eeprint("LINKING ERROR: the shader couldn't be linked to program:\n%s" % str(e))

        # detach the shaders from matter program
        gl.glDetachShader(self._program, self._vertex)
        gl.glDetachShader(self._program, self._fragment)

    def get_uniform_location(self, name: str):
        """
        gets and checks the uniform location with given name
        :param name: variable name (string)
        :return: location (int)
        """
        loc = gl.glGetUniformLocation(self._program, name)
        if loc < 0:
            eeprint("Uniform \"%s\" doesn't exist!"
                    "(Maybe the compilation optimized the shader by removing the unused uniform?)" % name)
        else:
            return loc

    def get_attribute_location(self, name: str):
        """
        gets and checks the attribute location with given name
        :param name: variable name (string)
        :return: location (int)
        """
        loc = gl.glGetAttribLocation(self._program, name)
        if loc < 0:
            eeprint("Attribute \"%s\" doesn't exist!"
                    "(Maybe the compilation optimized the shader by removing the unused attribute?)" % name)
        else:
            return loc

    def get_uniform(self, name, length):
        output = np.zeros(length, dtype=np.float32)
        loc = self.get_uniform_location(name)
        gl.glGetUniformfv(self._program, loc, output)
        return output

    def use(self):
        """
        sets the gl program to this one.
        :return:
        """
        gl.glBindVertexArray(self._vao)
        gl.glUseProgram(self._program)

    def set_projection_matrix(self, projection_matrix):
        """
        sets the projection matrix in the vertex shader program
        :param projection_matrix: 4x4 float32 projection matrix
        :return:
        """
        self.use()
        gpu_data = np.array(projection_matrix, dtype=np.float32).flatten()
        if len(gpu_data) != 16:
            eprint("ERROR: length of set_projection_matrix parameter not correct, expected 16 got %d " % len(gpu_data))
        else:
            loc = self.get_uniform_location("projection")
            gl.glUniformMatrix4fv(loc, 1, False, projection_matrix)

    def get_projection_matrix(self):
        """
        reads the projection matrix from the vertex shader
        :return:
        """
        return self.get_uniform("projection", 16)

    def set_view_matrix(self, view_matrix):
        """
        sets the view matrix in the vertex shader
        :param view_matrix: 4x4 float32 view matrix
        :return:
        """
        self.use()
        gpu_data = np.array(view_matrix, dtype=np.float32).flatten()
        if len(gpu_data) != 16:
            eprint("ERROR: length of set_view_matrix parameter not correct, expected 16 got %d " % len(gpu_data))
        else:
            loc = self.get_uniform_location("view")
            gl.glUniformMatrix4fv(loc, 1, False, view_matrix)

    def get_view_matrix(self):
        """
        reads the view matrix from the vertex shader
        :return:
        """
        return self.get_uniform("view", 16)

    def set_world_matrix(self, world_matrix):
        """
        sets the world matrix in the vertex shader
        :param world_matrix: 4x4 float32
        :return:
        """
        self.use()
        gpu_data = np.array(world_matrix, dtype=np.float32).flatten()
        if len(gpu_data) != 16:
            eprint("ERROR: length of set_world_matrix parameter not correct, expected 16 got %d " % len(gpu_data))
        else:
            loc = self.get_uniform_location("world")
            gl.glUniformMatrix4fv(loc, 1, False, world_matrix)

    def get_world_matrix(self):
        """
        reads the world matrix from the vertex shader
        :return:
        """
        return self.get_uniform("world", 16)

    def set_world_scaling(self, scaling):
        """
        sets the world scaling uniform in the vertex shader
        :param scaling:
        :return:
        """
        self.use()
        gpu_data = np.array(scaling, dtype=np.float32).flatten()
        if len(gpu_data) != 3:
            eprint("ERROR: length of set_world_scaling parameter not correct, expected 3 got %d " % len(gpu_data))
        else:
            loc = self.get_uniform_location("world_scaling")
            gl.glUniform3f(loc, *gpu_data)

    def get_world_scaling(self):
        """
        reads the world scaling vector from the vertex shader
        :return:
        """
        return self.get_uniform("world_scaling", 3)

    def rotate_light(self, angle: float):
        """
        rotates the parallel light source around the y axis
        :param angle: angle in degree
        :return:
        """
        self.use()
        self.light_angle += angle
        loc = self.get_uniform_location("light_direction")
        gl.glUniform3f(loc, np.sin(np.radians(self.light_angle)), 0.0, np.cos(np.radians(self.light_angle)))

    def get_light_direction(self):
        """
        reads the light direction vector from the vertex shader
        :return:
        """
        return self.get_uniform("light_direction", 3)

    def set_model_scaling(self, scaling):
        """
        sets the size scaling of the model
        :param scaling: 3d float tuple/array
        :return:
        """
        self.use()
        gpu_data = np.array(scaling, dtype=np.float32).flatten()
        if len(gpu_data) != 3:
            eprint("ERROR: length of set_model_scaling parameter not correct, expected 3 got %d " % len(gpu_data))
        else:
            loc = self.get_uniform_location("model_scaling")
            gl.glUniform3f(loc, *gpu_data)

    def get_model_scaling(self):
        """
        reads the model scaling vector from the vertex shader
        :return:
        """
        return self.get_uniform("model_scaling", 3)

    def set_ambient_light(self, ambient_light: float):
        """
        sets the ambient light strength
        :param ambient_light: float, minimal brightness / brightness in full shadow
        :return:
        """
        self.use()
        loc = self.get_uniform_location("ambient_light")
        gl.glUniform1f(loc, ambient_light)

    def get_ambient_light(self):
        """
        reads the ambient light value from the vertex shader
        :return:
        """
        return self.get_uniform("ambient_light", 1)

    def set_light_color(self, light_color):
        """
        sets the color of the light
        :param light_color: tuple/array, rgba format
        :return:
        """
        self.use()
        gpu_data = np.array(light_color, dtype=np.float32).flatten()
        if len(gpu_data) != 4:
            eprint("ERROR: length of set_light_color parameter not correct, expected 4 got %d " % len(gpu_data))
        else:
            loc = self.get_uniform_location("light_color")
            gl.glUniform4f(loc, *light_color)

    def get_light_color(self):
        """
        reads the light color from the vertex shader
        :return:
        """
        return self.get_uniform("light_color", 4)
