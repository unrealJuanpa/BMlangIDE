using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows.Forms;
using IronPython.Hosting;
using IronPython.Runtime.Operations;
using Microsoft.Scripting.Hosting;
using Microsoft.VisualBasic;

namespace BMlangIDE
{
    public partial class Form1 : Form
    {
        string rutapython = "C:\\Users\\unrea\\AppData\\Local\\Programs\\Python\\Python37\\python.exe";
        public Form1()
        {
            InitializeComponent();
        }

        private void textBox2_TextChanged(object sender, EventArgs e)
        {

        }

        private void button1_Click(object sender, EventArgs e)
        {
            //var res = Regex.Match(textBox2.Text, textBox1.Text).Success;
        }

        private void exitToolStripMenuItem_Click(object sender, EventArgs e)
        {
            Dispose();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            rutapython = Interaction.InputBox("Ingrese la ruta del ejecutable de python instalado en su sistema:", "Ruta de python", rutapython);
        }

        private async void saveToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (textBox2.Text.Length == 0 ) 
            {
                saveFileDialog1.ShowDialog();
                textBox2.Text = saveFileDialog1.FileName;
            }

            try
            {
                using (var fs = new StreamWriter(textBox2.Text))
                {
                    await fs.WriteAsync(textBox1.Text);
                }

                label2.Visible = false;
            }
            catch { }
        }

        private void openToolStripMenuItem_Click(object sender, EventArgs e)
        {
            openFileDialog1.ShowDialog();
            textBox2.Text = openFileDialog1.FileName;

            try
            {
                using (StreamReader file = new StreamReader(textBox2.Text))
                {
                    textBox1.Text = file.ReadToEnd();
                }

                label2.Visible = false;
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {
            label2.Visible = true;
        }

        private void selectAllToolStripMenuItem_Click(object sender, EventArgs e)
        {
            string s1 = Interaction.InputBox("Ingrese el texto a reemplazar:", "Reemplazo");
            
            if (s1.Length != 0)
            {
                string s2 = Interaction.InputBox("Ingrese el nuevo texto:", "Reemplazo");
                
                if (MessageBox.Show("Desea reemplazar \"" + s1 + "\" por \"" + s2 + "\"?", "Confirmación", MessageBoxButtons.OKCancel, MessageBoxIcon.Question) == DialogResult.OK)
                {
                    textBox1.Text = textBox1.Text.Replace(s1, s2);
                }
            }
        }

        private void runCodeToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (label2.Visible)
            {
                MessageBox.Show("Debe guardar primero el archivo!");
            }
            else
            {
                string path = System.AppContext.BaseDirectory;
                path = path.Replace("bin", "#");
                path = path.Split('#')[0] + "\\bmlang.py";

                try
                {
                    ScriptEngine engine = Python.CreateEngine();
                    Process.Start(rutapython, path + " " + textBox2.Text);
                }
                catch
                {
                    MessageBox.Show("Python no instalado o no presente en la ruta especificada!");
                }
            }
        }
    }
}
